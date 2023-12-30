"""
ASGI config for ITmanage project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os

import django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import it_purchase_list.routing
import it_purchase_list.routing

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ITmanage.settings")
django.setup()

# application = get_asgi_application()
application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            it_purchase_list.routing.websocket_urlpatterns
        )
    ),
})