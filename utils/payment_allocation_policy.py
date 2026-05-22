"""
سياسة تخصيص الدفعات — محاسبة ذمم (AR) على مستوى الجهة.

المبدأ (open-item على حساب الزبون):
- الالتزام (بيع/فاتورة/خدمة) = ذمة مستقلة.
- الدفعة الواردة = حق على حساب الزبون (تخفيض الذمة الإجمالية)، وليست إغلاق مستند بيع.
- لا توزيع تلقائي افتراضياً (PAYMENT_ALLOCATION_ENABLED=False).
"""

_CUSTOMER_DOCUMENT_ENTITY_TYPES = frozenset({"SALE", "INVOICE", "SERVICE", "PREORDER"})


def payment_auto_allocate_enabled() -> bool:
    """هل يُسمح بتخصيص الدفعات تلقائياً على مستندات مفتوحة؟"""
    try:
        from flask import current_app
        if bool(current_app.config.get("PAYMENT_ALLOCATION_ENABLED", False)):
            return True
    except Exception:
        pass
    try:
        from models import SystemSettings
        return bool(SystemSettings.get_setting("auto_allocate", False))
    except Exception:
        return False


def normalize_customer_payment_booking(
    entity_type: str,
    target_kwargs: dict,
    *,
    customer_id: int | None,
) -> tuple[str, dict]:
    """
    عند تعطيل التوزيع: تُسجَّل الدفعة على حساب الزبون فقط (customer_id)
    دون ربط sale_id / invoice_id / service_id / preorder_id.
    """
    if payment_auto_allocate_enabled():
        return entity_type, target_kwargs
    et = str(entity_type or "").upper()
    if et in _CUSTOMER_DOCUMENT_ENTITY_TYPES and customer_id:
        return "CUSTOMER", {"customer_id": int(customer_id)}
    return entity_type, target_kwargs
