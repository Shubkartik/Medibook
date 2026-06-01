from django.contrib import admin
from .models import ChatRoom, Message


# Inline display of messages within ChatRoom admin
class MessageInline(admin.TabularInline):
    model = Message
    extra = 0  # No extra empty forms
    readonly_fields = ['timestamp']  # Timestamp shouldn't be editable


@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    # Columns in list view
    list_display = ['appointment', 'patient', 'doctor', 'created_at', 'is_active']
    # Filter sidebar options
    list_filter = ['is_active', 'created_at']
    # Searchable fields
    search_fields = ['patient__username', 'doctor__username']
    # Show messages inline within chat room
    inlines = [MessageInline]


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    # Columns in list view
    list_display = ['sender', 'room', 'content_preview', 'timestamp', 'is_read']
    # Filter sidebar options
    list_filter = ['is_read', 'timestamp']
    # Searchable fields
    search_fields = ['sender__username', 'content']
    
    # Show first 50 characters of message content
    def content_preview(self, obj):
        return obj.content[:50]
    content_preview.short_description = 'Message Preview'  # Column header name