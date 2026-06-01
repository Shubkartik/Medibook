import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import ChatRoom, Message


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Get room ID from URL and create group name
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'
        self.user = self.scope['user']
        
        # Reject unauthenticated users
        if not self.user.is_authenticated:
            await self.close()
            return
        
        # Reject non-members of the chat room
        is_member = await self.is_room_member()
        if not is_member:
            await self.close()
            return
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        # Accept WebSocket connection
        await self.accept()
    
    async def disconnect(self, close_code):
        # Leave room group on disconnect
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
    
    async def receive(self, text_data):
        # Parse incoming JSON message
        data = json.loads(text_data)
        message_content = data.get('message', '').strip()
        
        # Ignore empty messages
        if not message_content:
            return
        
        # Save message to database
        message = await self.save_message(message_content)
        
        # Broadcast message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',  # Calls chat_message method
                'message': message_content,
                'sender_id': self.user.id,
                'sender_name': self.user.get_full_name(),
                'timestamp': message.timestamp.strftime('%I:%M %p'),
            }
        )
    
    async def chat_message(self, event):
        # Send message to WebSocket (received from group)
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message': event['message'],
            'sender_id': event['sender_id'],
            'sender_name': event['sender_name'],
            'timestamp': event['timestamp'],
        }))
    
    @database_sync_to_async
    def is_room_member(self):
        # Check if user is patient or doctor in this chat room
        try:
            room = ChatRoom.objects.get(id=self.room_id)
            return self.user in [room.patient, room.doctor]
        except ChatRoom.DoesNotExist:
            return False
    
    @database_sync_to_async
    def save_message(self, content):
        # Save message to database synchronously
        room = ChatRoom.objects.get(id=self.room_id)
        message = Message.objects.create(
            room=room,
            sender=self.user,
            content=content
        )
        return message