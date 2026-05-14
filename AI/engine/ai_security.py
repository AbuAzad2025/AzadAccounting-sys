"""AI security helpers.

This module protects secrets and sensitive operational information in AI replies.
It is intentionally permission-based and keeps the public function names stable
because the local AI response engine imports them directly.
"""

from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone
from typing import Any, Dict

from flask_login import current_user

from permissions_config.enums import SystemPermissions


SENSITIVE_KEYWORDS = {
    "passwords": ["password", "passwd", "pwd", "كلمة مرور", "كلمة السر", "رمز سري"],
    "api_keys": ["api key", "api_key", "secret_key", "secret key", "token", "مفتاح api", "مفتاح واجهة"],
    "database": ["database_url", "db_uri", "connection_string", "رابط قاعدة البيانات", "اتصال قاعدة البيانات"],
    "security": ["csrf", "session_key", "encryption key", "hash", "salt", "مفتاح التشفير"],
    "financial_details": ["balance_details", "رصيد تفصيلي", "حساب بنكي", "bank account", "iban"],
    "user_data": ["email", "phone", "address", "بريد", "هاتف", "عنوان"],
}

OWNER_ONLY_TOPICS = {
    "api_keys",
    "api key",
    "database_url",
    "connection_string",
    "system_configuration",
    "backup_locations",
    "encryption_keys",
    "secret_key",
    "groq_api",
    "master key",
    "ماستر كي",
}


def _is_authenticated_user() -> bool:
    return bool(getattr(current_user, "is_authenticated", False))


def _has_permission(permission: Any) -> bool:
    checker = getattr(current_user, "has_permission", None)
    if not callable(checker):
        return False
    perm_value = getattr(permission, "value", permission)
    for candidate in (perm_value, str(perm_value)):
        try:
            if checker(candidate):
                return True
        except Exception:
            continue
    return False


def is_owner() -> bool:
    """Return whether the current user has owner-level privileges."""
    if not _is_authenticated_user():
        return False
    try:
        return bool(
            getattr(current_user, "is_system_account", False)
            or getattr(current_user, "is_system", False)
            or getattr(current_user, "username", None) == "__OWNER__"
            or _has_permission(SystemPermissions.ACCESS_OWNER_DASHBOARD)
        )
    except Exception:
        return False


def is_super_admin() -> bool:
    return is_owner()


def is_manager() -> bool:
    """Return whether the current user has administrative reporting/management access."""
    if is_owner():
        return True
    if not _is_authenticated_user():
        return False
    return any(
        _has_permission(perm)
        for perm in (
            SystemPermissions.VIEW_REPORTS,
            SystemPermissions.MANAGE_SALES,
            SystemPermissions.MANAGE_USERS,
            SystemPermissions.MANAGE_AI,
        )
    )


def get_user_role_name() -> str:
    if is_owner():
        return "Owner"
    if is_manager():
        return "Admin"
    if _is_authenticated_user():
        return "User"
    return "Guest"


def is_sensitive_query(message: str) -> Dict[str, Any]:
    """Detect whether a query asks for sensitive data."""
    text = (message or "").lower()
    sensitive_found = []

    for category, keywords in SENSITIVE_KEYWORDS.items():
        for keyword in keywords:
            if keyword.lower() in text:
                sensitive_found.append({"category": category, "keyword": keyword})

    owner_only = any(topic.lower().replace("_", " ") in text for topic in OWNER_ONLY_TOPICS)

    return {
        "is_sensitive": bool(sensitive_found),
        "is_owner_only": owner_only,
        "found": sensitive_found,
        "requires_owner": owner_only,
        "requires_manager": bool(sensitive_found) and not owner_only,
    }


def filter_sensitive_data(data: Dict[str, Any], user_role: str = "") -> Dict[str, Any]:
    """Mask sensitive values from dictionaries unless the current user is owner."""
    if is_owner() or not isinstance(data, dict):
        return data

    filtered: Dict[str, Any] = {}
    for key, value in data.items():
        key_text = str(key).lower()
        blocked = any(keyword.lower() in key_text for keywords in SENSITIVE_KEYWORDS.values() for keyword in keywords)
        filtered[key] = "***HIDDEN***" if blocked else value
    return filtered


def get_security_response(message: str, sensitivity: Dict[str, Any]) -> str:
    """Return a safe refusal/explanation for sensitive requests when needed."""
    role = get_user_role_name()

    if sensitivity.get("requires_owner") and not is_owner():
        return (
            "🔒 **معلومات محمية**\n\n"
            "⚠️ هذه المعلومات متاحة للمالك فقط.\n\n"
            f"**دورك الحالي:** {role}\n"
            "**المطلوب:** access_owner_dashboard\n\n"
            "💡 إذا كنت بحاجة لهذه المعلومات، تواصل مع مالك النظام."
        )

    if sensitivity.get("is_sensitive") and not is_manager():
        return (
            "🔒 **معلومات حساسة**\n\n"
            "⚠️ هذه المعلومات تتطلب صلاحيات إدارية مناسبة.\n\n"
            f"**دورك الحالي:** {role}\n"
            "**المطلوب:** صلاحيات إدارية مثل view_reports أو manage_users."
        )

    return ""


def log_security_event(message: str, sensitivity: Dict[str, Any], response_type: str) -> None:
    """Append a compact AI security event to a local JSONL log."""
    try:
        os.makedirs("AI/data", exist_ok=True)
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "user": getattr(current_user, "username", "anonymous"),
            "role": get_user_role_name(),
            "query": (message or "")[:200],
            "sensitivity": sensitivity,
            "response_type": response_type,
        }
        with open("AI/data/ai_security_events.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")
    except Exception:
        pass


def sanitize_response(response: str) -> str:
    """Remove obvious secret patterns from AI responses for non-owner users."""
    text = str(response or "")
    if is_owner():
        return text

    patterns = [
        (r"password[:=\s]+[^\s,;]+", "password: ***"),
        (r"api[_\s-]?key[:=\s]+[^\s,;]+", "api_key: ***"),
        (r"secret[_\s-]?key[:=\s]+[^\s,;]+", "secret_key: ***"),
        (r"token[:=\s]+[^\s,;]+", "token: ***"),
        (r"sk-[A-Za-z0-9_\-]{10,}", "sk-***"),
        (r"postgres(?:ql)?://[^\s]+", "postgresql://***"),
        (r"mysql://[^\s]+", "mysql://***"),
    ]

    sanitized = text
    for pattern, replacement in patterns:
        sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)
    return sanitized


__all__ = [
    "is_owner",
    "is_super_admin",
    "is_manager",
    "get_user_role_name",
    "is_sensitive_query",
    "filter_sensitive_data",
    "get_security_response",
    "log_security_event",
    "sanitize_response",
]
