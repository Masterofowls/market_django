"""Production settings for Fly.io + Supabase Postgres."""

import os

from config.settings.base import *  # noqa: F403

DEBUG = False

# Fly terminates TLS at the edge; avoid redirect loops on internal health checks.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=False)  # noqa: F405
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Fly private health checks hit the machine IP as Host (not the public hostname).
if os.environ.get("FLY_APP_NAME"):
    ALLOWED_HOSTS = ["*"]  # noqa: F405

# Manifest storage can crash collectstatic on missing hashed refs in prod.
STORAGES["staticfiles"] = {  # noqa: F405
    "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
}

if DATABASES["default"].get("ENGINE", "").endswith("postgresql"):  # noqa: F405
    DATABASES["default"]["OPTIONS"] = {  # noqa: F405
        **DATABASES["default"].get("OPTIONS", {}),  # noqa: F405
        "sslmode": "require",
    }
