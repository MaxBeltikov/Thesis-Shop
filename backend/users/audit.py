from __future__ import annotations

from typing import Any

from .models import ActionLog


def client_ip(request) -> str:
    if not request:
        return ""
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        return xff.split(",")[0].strip()[:45]
    return (request.META.get("REMOTE_ADDR") or "")[:45]


def log_action(
    user,
    action: str,
    entity_type: str,
    entity_id: int,
    request=None,
    details: dict[str, Any] | None = None,
) -> None:
    ActionLog.objects.create(
        user=user if user and user.is_authenticated else None,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details or None,
        ip_address=client_ip(request),
    )
