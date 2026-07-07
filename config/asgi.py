import os

from django.core.asgi import get_asgi_application

# Default to production settings for ASGI hosting; allow override via env var.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.prod")

application = get_asgi_application()
