from pathlib import Path
import os
from datetime import timedelta
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent

load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "django-insecure-change-me")

DEBUG = False

ALLOWED_HOSTS = (
    os.getenv("DJANGO_ALLOWED_HOSTS", "").split(",")
    if os.getenv("DJANGO_ALLOWED_HOSTS")
    else []
)

INSTALLED_APPS = [
    "jazzmin",

    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",

    "import_export",

    "apps.accounts",
    "apps.schools",
    "apps.fees",
    "apps.results",
    "apps.document",
    "apps.plans",
    "apps.core",
    "apps.attendance",


    "admin_honeypot",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    'django_auto_logout.middleware.auto_logout',
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                'django_auto_logout.context_processors.auto_logout_client',
            ],
        },
    },
]

# Defined in dev.py / prod.py
DATABASES = {}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kolkata"

USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "accounts.User"

LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "accounts:role_redirect"
LOGOUT_REDIRECT_URL = "core:home"


# django-auto-logout package
AUTO_LOGOUT = {
    'IDLE_TIME': timedelta(minutes=90),
    'SESSION_TIME': timedelta(hours=12),
    'MESSAGE': 'Your session has expired due to inactivity. Please login again to continue.',
    'REDIRECT_TO_LOGIN_IMMEDIATELY': True,
}


# ----------------------------------------------------
# Site
# ----------------------------------------------------

SITE_URL = os.getenv(
    "SITE_URL",
    "http://localhost:8000",
)

# ----------------------------------------------------
# Email
# ----------------------------------------------------

EMAIL_BACKEND = os.getenv(
    "EMAIL_BACKEND",
    "django.core.mail.backends.console.EmailBackend",
)

EMAIL_HOST = os.getenv(
    "EMAIL_HOST",
    "smtp.gmail.com",
)

EMAIL_PORT = int(
    os.getenv("EMAIL_PORT", 587)
)

EMAIL_USE_TLS = (
    os.getenv("EMAIL_USE_TLS", "True").lower() == "true"
)

EMAIL_USE_SSL = (
    os.getenv("EMAIL_USE_SSL", "False").lower() == "true"
)

EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")

DEFAULT_FROM_EMAIL = os.getenv(
    "DEFAULT_FROM_EMAIL",
    "School ERP <noreply@example.com>",
)

SERVER_EMAIL = DEFAULT_FROM_EMAIL

#--- Logging settings
LOG_DIR = BASE_DIR / "logs"

LOG_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,

    "formatters": {
        "seed": {
            "format": "{asctime} | {levelname} | {message}",
            "style": "{",
        },
    },

    "handlers": {
        "seed_users_file": {
            "class": "logging.FileHandler",
            "filename": BASE_DIR / "logs" / "seed_users.log",
            "formatter": "seed",
            "level": "INFO",
        },

        "seed_documents_file": {
            "class": "logging.FileHandler",
            "filename": BASE_DIR / "logs" / "seed_documents.log",
            "formatter": "seed",
            "level": "INFO",
        },
    },

    "loggers": {
        "seed_users": {
            "handlers": [
                "seed_users_file",
            ],
            "level": "INFO",
            "propagate": False,
        },

        "seed_documents": {
            "handlers": [
                "seed_documents_file",
            ],
            "level": "INFO",
            "propagate": False,
        },
    },
}



from .jazz import *