"""Dynamic user guide knowledge for the AI assistant.

No route is treated as true unless it is found through ai_auto_discovery. Static
text is used only for workflow explanation, not as a source of live URLs.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

MODULES: Dict[str, Dict[str, Any]] = {
    "customers": {"title": "العملاء", "keywords": ["عميل", "customer", "زبون"], "description": "إدارة العملاء وأرصدة العملاء وكشوف الحساب.", "route_keywords": ["customers", "customer"], "create_keywords": ["customers create", "customer add"], "fields": {"name": "اسم العميل", "phone": "رقم الهاتف", "email": "البريد الإلكتروني", "address": "العنوان", "opening_balance": "الرصيد الافتتاحي", "notes": "ملاحظات"}, "steps": ["افتح صفحة العملاء", "اختر إضافة عميل إن كان الزر متاحًا حسب صلاحيتك", "أدخل الاسم ورقم الهاتف", "راجع الرصيد الافتتاحي إن وجد", "اضغط حفظ"]},
    "suppliers": {"title": "الموردين", "keywords": ["مورد", "supplier", "vendor"], "description": "إدارة الموردين وكشوف حساباتهم.", "route_keywords": ["suppliers", "vendors"], "create_keywords": ["suppliers create", "vendor add"], "fields": {"name": "اسم المورد", "phone": "رقم الهاتف", "email": "البريد الإلكتروني", "address": "العنوان", "opening_balance": "الرصيد الافتتاحي", "notes": "ملاحظات"}},
    "products": {"title": "المنتجات", "keywords": ["منتج", "product", "قطعة", "بضاعة"], "description": "إدارة المنتجات وقطع الغيار والأسعار والمخزون.", "route_keywords": ["products", "items"], "create_keywords": ["products create", "product add"], "fields": {"name": "اسم المنتج", "sku": "رمز المنتج", "barcode": "الباركود", "price": "سعر البيع", "selling_price": "سعر البيع", "purchase_price": "سعر الشراء/التكلفة", "min_qty": "الحد الأدنى"}},
    "sales": {"title": "المبيعات", "keywords": ["بيع", "مبيعات", "sale", "sales", "فاتورة"], "description": "إدارة المبيعات وفواتير البيع وتأثيرها على المخزون والذمم.", "route_keywords": ["sales"], "create_keywords": ["sales create", "sale new"], "steps": ["اختر العميل", "اختر المستودع", "أضف المنتجات والكميات", "راجع الخصم والضريبة من إعدادات النظام", "احفظ الفاتورة", "اطبعها عند الحاجة"]},
    "payments": {"title": "الدفعات", "keywords": ["دفعة", "payment", "دفع"], "description": "إدارة الدفعات الواردة والصادرة.", "route_keywords": ["payments"], "create_keywords": ["payments create", "payment add"], "fields": {"direction": "IN أو OUT", "method": "طريقة الدفع", "entity_type": "نوع الجهة", "amount": "المبلغ", "reference": "مرجع", "notes": "ملاحظات"}},
    "warehouses": {"title": "المستودعات", "keywords": ["مخزن", "warehouse", "مستودع", "مخزون"], "description": "إدارة المستودعات وحركة المخزون.", "route_keywords": ["warehouses", "inventory"], "create_keywords": ["warehouse create", "warehouses add"]},
    "expenses": {"title": "المصروفات", "keywords": ["مصروف", "expense", "نفقة"], "description": "تسجيل ومتابعة المصروفات.", "route_keywords": ["expenses"], "create_keywords": ["expenses create", "expense add"], "fields": {"amount": "المبلغ", "description": "الوصف", "date": "التاريخ", "payment_method": "طريقة الدفع", "reference": "المرجع"}},
    "services": {"title": "الصيانة", "keywords": ["صيانة", "service", "ورشة"], "description": "إدارة طلبات الصيانة ومراحل العمل وقطع الغيار.", "route_keywords": ["services", "service requests"], "create_keywords": ["services create", "service request create"], "fields": {"customer_id": "العميل", "vehicle_model": "موديل المركبة", "vehicle_vrn": "رقم المركبة", "problem_description": "وصف العطل", "mechanic_id": "المسؤول", "estimated_cost": "التكلفة المتوقعة"}},
    "reports": {"title": "التقارير", "keywords": ["تقرير", "report"], "description": "تقارير مالية وتشغيلية حسب الصلاحيات.", "route_keywords": ["reports"], "create_keywords": []},
    "general_ledger": {"title": "دفتر الأستاذ", "keywords": ["محاسب", "قيد", "gl", "ledger"], "description": "دفتر الأستاذ والقيود المحاسبية.", "route_keywords": ["gl", "ledger"], "create_keywords": []},
}

GUIDE_MODULE_KEYS = list(MODULES.keys())
COMPLETE_USER_GUIDE = {"system_name": "نظام أزاد لإدارة الكراج والمحاسبة", "version": "غير محدد - اقرأ الإصدار من إعدادات النظام عند الحاجة", **MODULES}


def _find_route(keywords) -> Optional[str]:
    try:
        from AI.engine.ai_auto_discovery import find_route_by_keyword
        for keyword in keywords or []:
            info = find_route_by_keyword(keyword)
            if info and info.get("matches"):
                route = info["matches"][0]
                return route.get("url") or route.get("path") or route.get("rule")
    except Exception:
        pass
    return None


class UserGuideMaster:
    def __init__(self):
        self.guide = COMPLETE_USER_GUIDE
        self.shortcuts = self._build_shortcuts()

    def answer_question(self, question: str) -> Dict[str, Any]:
        question = str(question or "")
        question_lower = question.lower()
        for key, module in MODULES.items():
            if any(word in question_lower for word in module.get("keywords", [])):
                if key == "general_ledger":
                    return self._explain_gl(question)
                return self._module_response(key, question)
        return self._general_help()

    def _module_response(self, key: str, question: str = "") -> Dict[str, Any]:
        module = MODULES[key]
        wants_create = any(word in question for word in ["إضافة", "اضافة", "أضف", "اضف", "إنشاء", "انشاء"]) or any(word in question.lower() for word in ["add", "create", "new"])
        route = _find_route(module.get("create_keywords") if wants_create else module.get("route_keywords"))
        payload = {"topic": module["title"], "description": module.get("description"), "route": route or "غير مفهرس حالياً", "route_source": "ai_auto_discovery" if route else "not_found"}
        if module.get("steps"):
            payload["steps"] = module["steps"]
        if module.get("fields"):
            payload["fields"] = module["fields"]
        if key == "sales":
            payload["calculations"] = {"subtotal": "مجموع البنود", "discount": "الخصم", "net": "الصافي", "vat": "ضريبة حسب إعدادات النظام", "total": "الإجمالي النهائي"}
            payload["stock_effect"] = "عادة يتم خصم الكمية من المستودع المختار عند تأكيد البيع حسب إعدادات النظام."
        if key in {"customers", "suppliers"}:
            payload["tips"] = ["تفسير موجب/سالب الرصيد يعتمد على سياسة النظام", "راجع الرصيد الافتتاحي قبل الحفظ"]
        return payload

    def _explain_gl(self, question: str) -> Dict[str, Any]:
        route = _find_route(MODULES["general_ledger"].get("route_keywords"))
        return {"topic": "دفتر الأستاذ العام", "description": MODULES["general_ledger"]["description"], "route": route or "غير مفهرس حالياً", "route_source": "ai_auto_discovery" if route else "not_found", "concepts": {"chart_of_accounts": "دليل الحسابات الفعلي يجب قراءته من النظام", "gl_entries": "القيود المحاسبية ويجب أن تكون متوازنة", "gl_batch": "مجموعة قيود مرتبطة بمعاملة"}}

    def _build_shortcuts(self) -> Dict[str, str]:
        return {key: (_find_route(value.get("route_keywords")) or "غير مفهرس حالياً") for key, value in MODULES.items()}

    def _general_help(self) -> Dict[str, Any]:
        return {"system_name": COMPLETE_USER_GUIDE["system_name"], "version": COMPLETE_USER_GUIDE["version"], "modules": GUIDE_MODULE_KEYS, "message": "اسألني عن العملاء، الموردين، المنتجات، المبيعات، الدفعات، المخازن، المصروفات، الصيانة، التقارير، أو دفتر الأستاذ."}


_guide_master = None


def get_user_guide_master() -> UserGuideMaster:
    global _guide_master
    if _guide_master is None:
        _guide_master = UserGuideMaster()
    return _guide_master


__all__ = ["UserGuideMaster", "get_user_guide_master", "COMPLETE_USER_GUIDE", "GUIDE_MODULE_KEYS"]
