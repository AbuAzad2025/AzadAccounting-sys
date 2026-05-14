"""User guide knowledge for the AI assistant.

The guide is intentionally concise and conservative. It should help users find
pages and understand workflows without hard-coding tax rates, inflated version
claims, or balance-sign assumptions that may differ by installation.
"""

from __future__ import annotations

from typing import Any, Dict


COMPLETE_USER_GUIDE: Dict[str, Any] = {
    "system_name": "نظام أزاد لإدارة الكراج والمحاسبة",
    "version": "غير محدد - اقرأ الإصدار من إعدادات النظام عند الحاجة",
    "customers": {
        "description": "إدارة العملاء وأرصدة العملاء وكشوف الحساب.",
        "main_route": "/customers",
        "features": {
            "add_customer": {
                "route": "/customers/create",
                "fields": {"name": "اسم العميل", "phone": "رقم الهاتف", "email": "البريد الإلكتروني", "address": "العنوان", "opening_balance": "الرصيد الافتتاحي", "notes": "ملاحظات"},
                "steps": ["افتح صفحة العملاء", "اضغط إضافة عميل", "أدخل الاسم والهاتف", "راجع الرصيد الافتتاحي إن وجد", "اضغط حفظ"],
                "tips": ["تفسير موجب/سالب الرصيد يعتمد على سياسة النظام", "رقم الهاتف يفضل أن يكون فريدًا", "راجع الرصيد الافتتاحي قبل الحفظ"],
                "gl_effect": "قد ينشأ قيد افتتاحي حسب إعدادات النظام.",
            },
            "customer_statement": {"route": "/customers/<id>/statement", "description": "كشف حساب العميل", "shows": ["الرصيد الافتتاحي", "المبيعات/الفواتير", "الدفعات", "الرصيد النهائي"], "filters": ["من تاريخ", "إلى تاريخ", "نوع المعاملة"]},
        },
    },
    "suppliers": {
        "description": "إدارة الموردين وكشوف حساباتهم.",
        "main_route": "/suppliers",
        "features": {"add_supplier": {"route": "/suppliers/create", "fields": {"name": "اسم المورد", "phone": "رقم الهاتف", "email": "البريد الإلكتروني", "address": "العنوان", "opening_balance": "الرصيد الافتتاحي", "notes": "ملاحظات"}, "gl_effect": "قد ينشأ قيد افتتاحي حسب إعدادات النظام."}},
    },
    "products": {
        "description": "إدارة المنتجات وقطع الغيار والأسعار والمخزون.",
        "main_route": "/products",
        "features": {"add_product": {"route": "/products/create", "fields": {"name": "اسم المنتج", "sku": "رمز المنتج", "barcode": "الباركود", "cost_price": "سعر التكلفة", "selling_price": "سعر البيع", "min_quantity": "الحد الأدنى"}, "features": ["دعم الباركود", "ربط المنتج بالمخزون", "متابعة الحد الأدنى"]}},
    },
    "sales": {
        "description": "إدارة المبيعات وفواتير البيع وتأثيرها على المخزون والذمم.",
        "main_route": "/sales",
        "features": {
            "create_sale": {
                "route": "/sales/create",
                "steps": ["اختر العميل", "اختر المستودع", "أضف المنتجات والكميات", "راجع الخصم والضريبة من إعدادات النظام", "احفظ الفاتورة", "اطبعها عند الحاجة"],
                "calculations": {"subtotal": "مجموع البنود", "discount": "الخصم", "net": "الصافي", "vat": "ضريبة حسب إعدادات النظام", "total": "الإجمالي النهائي"},
                "gl_entries": {"note": "تُنشأ القيود حسب إعدادات دفتر الأستاذ ودليل الحسابات."},
                "stock_effect": "عادة يتم خصم الكمية من المستودع المختار عند تأكيد البيع.",
            },
            "view_sales": {"route": "/sales", "features": ["عرض المبيعات", "فلترة بالتاريخ", "البحث برقم الفاتورة أو العميل", "عرض الإجماليات حسب الصلاحيات"]},
        },
    },
    "payments": {
        "description": "إدارة الدفعات الواردة والصادرة.",
        "main_route": "/payments",
        "types": {"incoming": {"direction": "IN", "description": "دفعة واردة"}, "outgoing": {"direction": "OUT", "description": "دفعة صادرة"}},
        "payment_methods": {"CASH": "نقدي", "BANK": "بنكي", "CARD": "بطاقة", "CHECK": "شيك"},
        "features": {"create_payment": {"route": "/payments/create", "fields": {"direction": "IN أو OUT", "method": "طريقة الدفع", "entity_type": "نوع الجهة", "entity_id": "الجهة", "amount": "المبلغ", "reference": "مرجع", "notes": "ملاحظات"}}},
    },
    "warehouses": {
        "description": "إدارة المستودعات وحركة المخزون.",
        "main_route": "/warehouses",
        "types": {"MAIN": "رئيسي", "ONLINE": "متجر إلكتروني", "PARTNER": "شريك", "INVENTORY": "جرد", "EXCHANGE": "تبادل"},
        "features": {"stock_transfer": {"route": "/warehouses/transfer", "description": "نقل بضاعة بين مستودعات"}, "stock_adjustment": {"route": "/warehouses/adjust", "description": "تعديل مخزون بسبب جرد أو تلف أو فرق"}},
    },
    "expenses": {
        "description": "تسجيل ومتابعة المصروفات.",
        "main_route": "/expenses",
        "categories": ["رواتب", "إيجار", "كهرباء ومياه", "صيانة", "مواصلات", "قرطاسية", "أخرى"],
        "features": {"create_expense": {"route": "/expenses/create", "fields": {"category": "التصنيف", "amount": "المبلغ", "description": "الوصف", "date": "التاريخ", "payment_method": "طريقة الدفع", "reference": "المرجع"}, "gl_effect": "حسب إعدادات المصروف ووسيلة الدفع."}},
    },
    "services": {
        "description": "إدارة طلبات الصيانة ومراحل العمل وقطع الغيار.",
        "main_route": "/services",
        "workflow": {"1_create": "إنشاء طلب", "2_assign": "تعيين مسؤول", "3_start": "بدء العمل", "4_complete": "إكمال", "5_invoice": "فوترة عند الحاجة"},
        "statuses": {"pending": "معلق", "in_progress": "جاري العمل", "completed": "مكتمل", "cancelled": "ملغي"},
        "features": {"create_service": {"route": "/services/create", "fields": {"customer_id": "العميل", "car_info": "معلومات السيارة", "description": "وصف العطل", "mechanic_id": "المسؤول", "estimated_cost": "التكلفة المتوقعة"}}},
    },
    "reports": {
        "description": "تقارير مالية وتشغيلية حسب الصلاحيات.",
        "main_route": "/reports",
        "types": {"financial": ["ميزان المراجعة", "قائمة الدخل", "الميزانية", "التدفقات النقدية"], "sales": ["تقرير المبيعات", "أفضل العملاء", "أفضل المنتجات"], "inventory": ["تقرير المخزون", "حركة المخزون", "المخزون المنخفض"]},
    },
    "general_ledger": {
        "description": "دفتر الأستاذ والقيود المحاسبية.",
        "main_route": "/gl",
        "concepts": {"chart_of_accounts": {"description": "دليل الحسابات الفعلي يجب قراءته من النظام"}, "gl_entries": {"description": "القيود المحاسبية", "rule": "المدين = الدائن"}, "gl_batch": {"description": "مجموعة قيود مرتبطة بمعاملة"}},
        "features": {"view_gl": {"route": "/gl", "shows": "القيود المحاسبية"}, "account_ledger": {"route": "/gl/account/<account_code>", "shows": "حركة حساب محدد"}},
    },
}


GUIDE_MODULE_KEYS = ["customers", "suppliers", "products", "sales", "payments", "warehouses", "expenses", "services", "reports", "general_ledger"]


class UserGuideMaster:
    def __init__(self):
        self.guide = COMPLETE_USER_GUIDE
        self.shortcuts = self._build_shortcuts()

    def answer_question(self, question: str) -> Dict[str, Any]:
        question = str(question or "")
        question_lower = question.lower()
        if any(word in question_lower for word in ["عميل", "customer", "زبون"]):
            return self._explain_customers(question)
        if any(word in question_lower for word in ["مورد", "supplier"]):
            return self._module_response("suppliers", "الموردين")
        if any(word in question_lower for word in ["منتج", "product", "قطعة", "بضاعة"]):
            return self._module_response("products", "المنتجات")
        if any(word in question_lower for word in ["بيع", "مبيعات", "sale", "فاتورة"]):
            return self._explain_sales(question)
        if any(word in question_lower for word in ["دفعة", "payment", "دفع"]):
            return self._module_response("payments", "الدفعات")
        if any(word in question_lower for word in ["مخزن", "warehouse", "مستودع"]):
            return self._module_response("warehouses", "المخازن")
        if any(word in question_lower for word in ["مصروف", "expense"]):
            return self._module_response("expenses", "المصروفات")
        if any(word in question_lower for word in ["صيانة", "service", "ورشة"]):
            return self._module_response("services", "الصيانة")
        if any(word in question_lower for word in ["تقرير", "report"]):
            return self._module_response("reports", "التقارير")
        if any(word in question_lower for word in ["محاسب", "قيد", "gl", "ledger"]):
            return self._explain_gl(question)
        return self._general_help()

    def _explain_customers(self, question: str) -> Dict[str, Any]:
        customers = self.guide["customers"]
        if any(word in question for word in ["إضافة", "اضافة", "أضف", "اضف"]) or "add" in question.lower():
            feature = customers["features"]["add_customer"]
            return {"topic": "إضافة عميل جديد", "route": feature["route"], "steps": feature["steps"], "fields": feature["fields"], "tips": feature["tips"], "gl_effect": feature["gl_effect"]}
        if "كشف" in question or "statement" in question.lower():
            feature = customers["features"]["customer_statement"]
            return {"topic": "كشف حساب العميل", "description": feature["description"], "route": feature["route"], "shows": feature["shows"], "filters": feature["filters"]}
        return {"topic": "إدارة العملاء", "description": customers["description"], "route": customers["main_route"], "features": list(customers["features"].keys())}

    def _explain_sales(self, question: str) -> Dict[str, Any]:
        sales = self.guide["sales"]
        if any(word in question for word in ["إنشاء", "انشاء", "إضافة", "اضافة"]) or any(word in question.lower() for word in ["create", "add"]):
            feature = sales["features"]["create_sale"]
            return {"topic": "إنشاء فاتورة بيع", "route": feature["route"], "steps": feature["steps"], "calculations": feature["calculations"], "gl_entries": feature["gl_entries"], "stock_effect": feature["stock_effect"]}
        return {"topic": "المبيعات", "description": sales["description"], "route": sales["main_route"], "features": list(sales["features"].keys())}

    def _explain_gl(self, question: str) -> Dict[str, Any]:
        gl = self.guide["general_ledger"]
        return {"topic": "دفتر الأستاذ العام", "description": gl["description"], "route": gl["main_route"], "concepts": gl["concepts"], "features": gl["features"]}

    def _module_response(self, key: str, topic: str) -> Dict[str, Any]:
        module = self.guide[key]
        return {"topic": topic, "description": module.get("description"), "route": module.get("main_route"), "features": list((module.get("features") or {}).keys()), "summary": {k: v for k, v in module.items() if k not in {"features"} and k in {"types", "workflow", "statuses", "categories"}}}

    def _build_shortcuts(self) -> Dict[str, str]:
        return {"add_customer": "/customers/create", "add_supplier": "/suppliers/create", "add_product": "/products/create", "create_sale": "/sales/create", "create_payment": "/payments/create", "view_reports": "/reports", "view_gl": "/gl"}

    def _general_help(self) -> Dict[str, Any]:
        return {"system_name": self.guide["system_name"], "version": self.guide["version"], "modules": GUIDE_MODULE_KEYS, "message": "اسألني عن العملاء، الموردين، المنتجات، المبيعات، الدفعات، المخازن، المصروفات، الصيانة، التقارير، أو دفتر الأستاذ."}


_guide_master = None


def get_user_guide_master() -> UserGuideMaster:
    global _guide_master
    if _guide_master is None:
        _guide_master = UserGuideMaster()
    return _guide_master


__all__ = ["UserGuideMaster", "get_user_guide_master", "COMPLETE_USER_GUIDE", "GUIDE_MODULE_KEYS"]
