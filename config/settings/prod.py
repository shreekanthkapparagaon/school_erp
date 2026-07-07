"""
Production settings for the Django project.

This module imports `base.py` and applies production-safe overrides. In
production the `DJANGO_SETTINGS_MODULE` environment variable should be set to
`config.settings.prod` and a real `DJANGO_SECRET_KEY` must be provided.
"""
from .base import *  # noqa: F401,F403

import os

# In production, require an explicit secret key.
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")
if not SECRET_KEY:
	raise RuntimeError("DJANGO_SECRET_KEY environment variable must be set in production")

# Disable debug in production
DEBUG = False

# ALLOWED_HOSTS must be explicitly provided in production
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "").split(",") if os.environ.get("DJANGO_ALLOWED_HOSTS") else []

# Production database settings (example): set via environment variables
# Consider using a URL parser (dj-database-url) if needed.
MEDIA_URL = ""
