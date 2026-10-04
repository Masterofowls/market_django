"""Shared Django settings for the electronic marketplace."""

from __future__ import annotations

from pathlib import Path

import dj_database_url
import environ

BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env(
    DJANGO_DEBUG=(bool, False),
    DJANGO_ALLOWED_HOSTS=(list, ["localhost", "127.0.0.1"]),
    DJANGO_CSRF_TRUSTED_ORIGINS=(list, []),
    MFA_WEBAUTHN_ALLOW_INSECURE_ORIGIN=(bool, False),
)

environ.Env.read_env(BASE_DIR / ".env", overwrite=True)

SECRET_KEY = env("DJANGO_SECRET_KEY", default="dev-insecure-change-me")
DEBUG = env("DJANGO_DEBUG")
ALLOWED_HOSTS = env("DJANGO_ALLOWED_HOSTS")
CSRF_TRUSTED_ORIGINS = env("DJANGO_CSRF_TRUSTED_ORIGINS")

SITE_ID = 1
X_FRAME_OPTIONS = "SAMEORIGIN"

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "django.contrib.humanize",
    # Custom user must load before cms / allauth consumers
    "apps.accounts",
    # Auth
    "allauth",
    "allauth.account",
    "allauth.mfa",
    "allauth.socialaccount",
    # API / tooling
    "rest_framework",
    "rest_framework.authtoken",
    "django_filters",
    "drf_spectacular",
    "corsheaders",
    "import_export",
    "imagekit",
    "health_check",
    # Domain apps (before CMS plugins that may reference content)
    "apps.core",
    "apps.catalog",
    "apps.cart",
    "apps.orders",
    "apps.favourites",
    "apps.reviews.apps.ReviewsConfig",
    "apps.recommendations",
    "apps.marketing",
    "apps.notifications",
    # CMS stack
    "cms",
    "menus",
    "treebeard",
    "sekizai",
    "filer",
    "easy_thumbnails",
    "djangocms_text_ckeditor",
    "djangocms_link",
    "djangocms_picture",
    "djangocms_file",
    "djangocms_style",
]

MIDDLEWARE = [
    "cms.middleware.utils.ApphookReloadMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "cms.middleware.user.CurrentUserMiddleware",
    "cms.middleware.page.CurrentPageMiddleware",
    "cms.middleware.toolbar.ToolbarMiddleware",
    "cms.middleware.language.LanguageCookieMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

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
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "sekizai.context_processors.sekizai",
                "cms.context_processors.cms_settings",
                "apps.core.context_processors.storefront",
            ],
        },
    },
]

_default_sqlite = f"sqlite:///{(BASE_DIR / 'db.sqlite3').as_posix()}"
_database_url = env("DATABASE_URL", default=_default_sqlite) or _default_sqlite
_is_postgres = _database_url.startswith(("postgres://", "postgresql://"))
DATABASES = {
    "default": dj_database_url.parse(
        _database_url,
        conn_max_age=600,
        ssl_require=env.bool("DATABASE_SSL_REQUIRE", default=False) and _is_postgres,
    )
}

AUTH_USER_MODEL = "accounts.User"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en"
LANGUAGES = [
    ("en", "English"),
]
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True
# Keep storefront URLs unprefixed for the default language.
PREFIX_DEFAULT_LANGUAGE = False

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

LOGIN_REDIRECT_URL = "/account/"
ACCOUNT_LOGOUT_REDIRECT_URL = "/"
LOGIN_URL = "/accounts/login/"
# Username login always; email login works when an email is present.
ACCOUNT_LOGIN_METHODS = {"username", "email"}
# Trailing "*" marks a field required — email has no "*" so it is optional.
ACCOUNT_SIGNUP_FIELDS = ["username*", "email", "password1*", "password2*"]
ACCOUNT_EMAIL_VERIFICATION = "optional"
ACCOUNT_EMAIL_VERIFICATION_BY_CODE_ENABLED = False
ACCOUNT_ADAPTER = "apps.accounts.adapters.AccountAdapter"

# Passkeys / MFA (django-allauth)
# Passkey signup needs mandatory verified email; keep login-only with optional email.
MFA_SUPPORTED_TYPES = ["totp", "webauthn", "recovery_codes"]
MFA_PASSKEY_LOGIN_ENABLED = True
MFA_PASSKEY_SIGNUP_ENABLED = False
MFA_WEBAUTHN_ALLOW_INSECURE_ORIGIN = env("MFA_WEBAUTHN_ALLOW_INSECURE_ORIGIN")

# Supabase project (API / future clients). Postgres still uses DATABASE_URL.
SUPABASE_URL = env("SUPABASE_URL", default="https://eadxantpovgupzwemomv.supabase.co")
SUPABASE_PUBLISHABLE_KEY = env("SUPABASE_PUBLISHABLE_KEY", default="")
SUPABASE_SECRET_KEY = env("SUPABASE_SECRET_KEY", default="")
SUPABASE_JWKS_URL = env(
    "SUPABASE_JWKS_URL",
    default=f"{SUPABASE_URL.rstrip('/')}/auth/v1/.well-known/jwks.json",
)

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.TokenAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticatedOrReadOnly",
    ],
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 24,
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "ElectroMarket API",
    "DESCRIPTION": "Electronic store marketplace API (DRF)",
    "VERSION": "1.0.0",
}

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=[])

CMS_TEMPLATES = [
    ("cms/home.html", "Home"),
    ("cms/page.html", "Content page"),
]
CMS_PERMISSION = True
CMS_PLACEHOLDER_CONF = {}

THUMBNAIL_HIGH_RESOLUTION = True
THUMBNAIL_PROCESSORS = (
    "easy_thumbnails.processors.colorspace",
    "easy_thumbnails.processors.autocrop",
    "filer.thumbnail_processors.scale_and_crop_with_subject_location",
    "easy_thumbnails.processors.filters",
)

EMAIL_BACKEND = env(
    "EMAIL_BACKEND",
    default="django.core.mail.backends.console.EmailBackend",
)
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="noreply@electromarket.local")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {name} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}

# Upstream django-cms / treebeard compatibility warning until Treebeard 6.
SILENCED_SYSTEM_CHECKS = ["treebeard.E001"]
