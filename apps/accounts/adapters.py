"""django-allauth adapters."""

from __future__ import annotations

from allauth.account.adapter import DefaultAccountAdapter


class AccountAdapter(DefaultAccountAdapter):
    """Allow username signup with optional email."""

    def is_open_for_signup(self, request):  # noqa: ANN001
        return True

    def clean_email(self, email: str) -> str:
        email = (email or "").strip()
        if not email:
            return ""
        return super().clean_email(email)
