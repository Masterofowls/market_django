"""Local development settings."""

from config.settings.base import *  # noqa: F403

DEBUG = True
ALLOWED_HOSTS = ["*"]
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
MFA_WEBAUTHN_ALLOW_INSECURE_ORIGIN = True
CORS_ALLOW_ALL_ORIGINS = True

STORAGES["staticfiles"] = {  # noqa: F405
    "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
}
