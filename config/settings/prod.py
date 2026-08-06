from .base import *

DEBUG = False

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.getenv("MARIADB_DATABASE"),
        "USER": os.getenv("MARIADB_USER"),
        "PASSWORD": os.getenv("MARIADB_PASSWORD"),
        "HOST": os.getenv("MARIADB_HOST", "localhost"),
        "PORT": os.getenv("MARIADB_PORT", "3306"),
        "CONN_MAX_AGE": 600,
        "OPTIONS": {
            "charset": "utf8mb4",
            "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

DEBUG = False

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

SECURE_PROXY_SSL_HEADER = (
    "HTTP_X_FORWARDED_PROTO",
    "https",
)

EMAIL_VERIFICATION_REQUIRED = True