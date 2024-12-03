import os
import django

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application

# Django sozlamalarini aniqlash
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "einvestment.settings")

# Django ASGI ilovasini boshlash
django_asgi_app = get_asgi_application()

# Middleware import qilish
from chat.middleware import UserAuthMiddleware  # Buni to'g'ri pathga o'zgartiring

# WebSocket URL'larini import qilish
from chat.routing import websocket_urlpatterns

# Django ilovasini initializatsiya qilish
django.setup()

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,  # HTTP uchun ASGI ilovasi
        "websocket": AllowedHostsOriginValidator(
            UserAuthMiddleware(  # UserAuthMiddleware qo'shish
                AuthMiddlewareStack(  # AuthMiddlewareStack bilan birga
                    URLRouter(websocket_urlpatterns)
                )
            )
        ),
    }
)
