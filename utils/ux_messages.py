"""رسائل موحّدة للأخطاء والتحذيرات والإرشادات — واجهة أزاد."""
from __future__ import annotations

import re
from typing import Any

FLASH_TITLES: dict[str, str] = {
    "success": "تم بنجاح",
    "danger": "خطأ",
    "error": "خطأ",
    "warning": "تنبيه",
    "info": "معلومة",
    "primary": "إشعار",
    "secondary": "إشعار",
}

FLASH_ICONS: dict[str, str] = {
    "success": "fa-check-circle",
    "danger": "fa-times-circle",
    "error": "fa-times-circle",
    "warning": "fa-exclamation-triangle",
    "info": "fa-info-circle",
    "primary": "fa-bell",
    "secondary": "fa-bell",
}

# رسائل قياسية — مفتاح → نص واضح مع إرشاد
STANDARD_MESSAGES: dict[str, str] = {
    "internal_error": (
        "تعذّر إكمال العملية. تحقق من البيانات وحاول مجدداً، "
        "أو تواصل مع مسؤول النظام إن استمر الخطأ."
    ),
    "validation_error": "يرجى مراجعة الحقول المظلّلة وتصحيحها قبل المتابعة.",
    "required_fields": "يرجى تعبئة جميع الحقول المطلوبة (*).",
    "permission_denied": "ليس لديك صلاحية تنفيذ هذا الإجراء. اطلب الصلاحية من المسؤول.",
    "not_found": "العنصر المطلوب غير موجود أو ربما تم حذفه.",
    "duplicate": "هذا السجل موجود مسبقاً. استخدم قيمة مختلفة.",
    "network_error": "تعذّر الاتصال بالخادم. تحقق من الشبكة وحاول مرة أخرى.",
    "session_expired": "انتهت الجلسة. سجّل الدخول مجدداً للمتابعة.",
    "csrf_error": "انتهت صلاحية النموذج. حدّث الصفحة وأعد المحاولة.",
    "saved": "تم حفظ البيانات بنجاح.",
    "deleted": "تم الحذف بنجاح.",
    "updated": "تم التحديث بنجاح.",
    "created": "تم الإنشاء بنجاح.",
    "cancelled": "تم إلغاء العملية.",
    "no_results": "لا توجد نتائج مطابقة لبحثك.",
    "confirm_delete": "هل أنت متأكد؟ لا يمكن التراجع عن الحذف.",
    "fx_missing": "لا يوجد سعر صرف متاح لهذه العملة. أضف سعراً في إدارة العملات.",
    "amount_positive": "المبلغ يجب أن يكون أكبر من صفر.",
    "date_invalid": "التاريخ غير صالح. تحقق من التنسيق (YYYY-MM-DD).",
    "check_due_before_issue": "تاريخ الاستحقاق لا يمكن أن يكون قبل تاريخ الشيك.",
}

# نصوص قديمة/مكررة → رسالة موحّدة
_MESSAGE_ALIASES: dict[str, str] = {
    "حدث خطأ داخلي": "internal_error",
    "حدث خطأ": "internal_error",
    "خطأ في إنشاء الفرع": "internal_error",
    "خطأ في تحديث الفرع": "internal_error",
    "يرجى ملء جميع الحقول المطلوبة": "required_fields",
    "يرجى تصحيح الحقول المظللة أدناه.": "validation_error",
    "ليس لديك صلاحية": "permission_denied",
}

_EMOJI_PREFIX = re.compile(r"^[\s✅❌⚠️ℹ️🔴🟢🟡🔵⭐📌💡]+")


def normalize_flash_category(category: str | None) -> str:
    c = (category or "info").strip().lower()
    mapping = {
        "error": "danger",
        "fail": "danger",
        "failed": "danger",
        "dangerous": "danger",
        "warn": "warning",
        "alert": "warning",
        "ok": "success",
        "done": "success",
        "message": "info",
    }
    c = mapping.get(c, c)
    if c not in FLASH_TITLES:
        return "info"
    return c


def msg(key: str, default: str = "") -> str:
    return STANDARD_MESSAGES.get(key, default or key)


def flash_title(category: str | None) -> str:
    return FLASH_TITLES.get(normalize_flash_category(category), "إشعار")


def flash_icon(category: str | None) -> str:
    return FLASH_ICONS.get(normalize_flash_category(category), "fa-info-circle")


def clean_flash_text(text: str | None) -> str:
    if text is None:
        return ""
    t = str(text).strip()
    if not t:
        return ""
    t = _EMOJI_PREFIX.sub("", t).strip()
    if t in _MESSAGE_ALIASES:
        return msg(_MESSAGE_ALIASES[t])
    for prefix, key in _MESSAGE_ALIASES.items():
        if t == prefix or t.startswith(prefix + "."):
            return msg(key)
    return t


def prepare_flash(category: str | None, message: str | None) -> dict[str, str]:
    cat = normalize_flash_category(category)
    body = clean_flash_text(message)
    return {
        "category": cat,
        "title": flash_title(cat),
        "icon": flash_icon(cat),
        "message": body,
    }


def api_payload(
    *,
    success: bool = False,
    message: str | None = None,
    key: str | None = None,
    errors: dict[str, Any] | list | None = None,
    **extra: Any,
) -> dict[str, Any]:
    """استجابة JSON موحّدة للواجهة."""
    text = msg(key) if key else clean_flash_text(message or "")
    if not text and not success:
        text = msg("internal_error")
    payload: dict[str, Any] = {
        "success": success,
        "message": text,
        "error": None if success else text,
    }
    if errors is not None:
        payload["errors"] = errors
    payload.update(extra)
    return payload


def flash_msg(category: str, message: str | None = None, *, key: str | None = None) -> None:
    """Flash موحّد — category: success|danger|warning|info أو مفتاح من UX_MSG."""
    from flask import flash

    cat = normalize_flash_category(category)
    text = msg(key) if key else clean_flash_text(message or "")
    if text:
        flash(text, cat)
