"""Root URL configuration."""

from __future__ import annotations

from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.static import serve
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from health_check.views import HealthCheckView

from config.api import api

urlpatterns = [
    path("api/v1/", include("config.api_urls")),
    path("api/ninja/", api.urls),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    # Fly health checks: skip DNS/Mail/Storage (machine hostname is not a DNS name).
    path(
        "ht/",
        HealthCheckView.as_view(
            checks=[
                "health_check.checks.Database",
                "health_check.checks.Cache",
            ]
        ),
        name="health-check",
    ),
    path("accounts/", include("allauth.urls")),
]

urlpatterns += i18n_patterns(
    path("admin/", admin.site.urls),
    path("pages/", include("cms.urls")),
    path("", include("apps.core.urls")),
    prefix_default_language=False,
)

# Always serve uploaded product images (WhiteNoise only covers STATIC, not MEDIA).
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    urlpatterns += [
        re_path(
            r"^media/(?P<path>.*)$",
            serve,
            {"document_root": settings.MEDIA_ROOT},
        ),
    ]
