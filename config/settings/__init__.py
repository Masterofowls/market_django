"""Load environment-specific Django settings."""

from __future__ import annotations

import os

_env = os.getenv("DJANGO_ENV", "local").lower()

if _env == "production":
    from config.settings.production import *  # noqa: F403
else:
    from config.settings.local import *  # noqa: F403
