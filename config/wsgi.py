import os

from django.core.wsgi import get_wsgi_application

# Default to production settings for WSGI hosting; allow override via env var.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.prod")

application = get_wsgi_application()
