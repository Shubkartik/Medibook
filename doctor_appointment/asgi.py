import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'doctor_appointment.settings')

# Initialize Django ASGI application early to ensure apps are loaded
django_asgi_app = get_asgi_application()

# Import WebSocket routes after Django setup
from chat.routing import websocket_urlpatterns

# Route protocols: HTTP and WebSocket
application = ProtocolTypeRouter({
    # HTTP handled by Django views
    "http": django_asgi_app,
    # WebSocket with security layers
    "websocket": AllowedHostsOriginValidator(  # Validate origin hosts
        AuthMiddlewareStack(  # Add user to scope
            URLRouter(
                websocket_urlpatterns  # WebSocket URL routes
            )
        )
    ),
})