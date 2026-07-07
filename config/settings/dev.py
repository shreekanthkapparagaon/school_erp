"""
Development settings for the Django project.

This module imports everything from `base.py` and then applies development
overrides. Use `manage.py` (which defaults to this settings module) when
running the development server or local management commands.
"""
from .base import *  # noqa: F401,F403

import os

# Use an environment-provided secret key if available, otherwise fall back to
# the base development key. This is convenient for local development.
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", SECRET_KEY)

# Development mode
DEBUG = True

# Allow local addresses by default; override via DJANGO_ALLOWED_HOSTS.
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
