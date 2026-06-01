from django.apps import AppConfig


class ChatConfig(AppConfig):
    # Default auto-incrementing primary key field type
    default_auto_field = 'django.db.models.BigAutoField'
    # App name (must match directory name)
    name = 'chat'
    # Human-readable name shown in Django admin
    verbose_name = 'Chat System'