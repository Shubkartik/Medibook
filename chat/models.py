from django.db import models
from django.contrib.auth.models import User
from appointments.models import Appointment


class ChatRoom(models.Model):
    """Chat room created when appointment is confirmed"""
    # One chat room per appointment
    appointment = models.OneToOneField(
        Appointment, 
        on_delete=models.CASCADE, 
        related_name='chat_room'
    )
    # Patient participating in chat
    patient = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='patient_chats'
    )
    # Doctor participating in chat
    doctor = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='doctor_chats'
    )
    # Auto-set when room is created
    created_at = models.DateTimeField(auto_now_add=True)
    # Whether chat is still active
    is_active = models.BooleanField(default=True)
    
    class Meta:
        # Ensure one chat room per appointment
        unique_together = ['appointment']
    
    def __str__(self):
        return f"Chat: {self.patient.username} - Dr. {self.doctor.username}"
    
    def get_unread_count(self, user):
        # Count unread messages not sent by the given user
        return self.messages.filter(
            is_read=False
        ).exclude(
            sender=user
        ).count()


class Message(models.Model):
    """Individual chat messages"""
    # Chat room this message belongs to
    room = models.ForeignKey(
        ChatRoom, 
        on_delete=models.CASCADE, 
        related_name='messages'
    )
    # User who sent the message
    sender = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='sent_messages'
    )
    # Message text content
    content = models.TextField()
    # Auto-set when message is sent
    timestamp = models.DateTimeField(auto_now_add=True)
    # Whether recipient has read the message
    is_read = models.BooleanField(default=False)
    
    class Meta:
        # Order messages by oldest first
        ordering = ['timestamp']
    
    def __str__(self):
        # Show first 50 characters of message
        return f"{self.sender.username}: {self.content[:50]}"