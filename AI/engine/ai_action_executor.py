"""AI Action Executor.

Safe executor for AI-assisted write operations. Destructive actions are not
exposed here; they are blocked by ai_permissions and intentionally omitted from
the action map. Constructors are built using actual SQLAlchemy column names so
minor model differences do not crash the AI path.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from typing import Any, Dict, Optional, Tuple

from extensions import db
from models import AuditLog


SAFE_ACTION_ALIASES = {
    "create_customer": "add_customer",
    "create_supplier": "add_supplier",
    "create_product": "add_product",
    "create_warehouse": "add_warehouse",
}


class ActionExecutor:
    """Execute explicitly allowed, non-destructive AI actions."""

    def __init__(self, user_id: int = None):
        self.user_id = user_id
        self.last_action = None
        self.errors = []

    def execute_action(self, action_type: str, params: Dict[str, Any]) -> Dict[str, Any]:
        try:
            normalized_action = SAFE_ACTION_ALIASES.get(str(action_type or "").strip().lower(), str(action_type or "").strip().lower())
            action_map = {
                "add_customer": self.add_customer,
                "add_supplier": self.add_supplier,
                "add_product": self.add_product,
                "create_sale": self.create_sale,
                "create_invoice": self.create_invoice,
                "create_payment": self.create_payment,
                "create_expense": self.create_expense,
                "create_service": self.create_service,
                "add_warehouse": self.add_warehouse,
                "transfer_stock": self.transfer_stock,
                "adjust_stock": self.adjust_stock,
            }

            action_func = action_map.get(normalized_action)
            if not action_func:
                return {
                    "success": False,
                    "message": f"❌ العملية '{action_type}' غير مسموحة أو غير معروفة للمساعد الذكي",
                    "available_actions": sorted(action_map.keys()),
                }

            from AI.engine.ai_permissions import can_ai_execute_action

            if not can_ai_execute_action(normalized_action, ""):
                return {"success": False, "message": "❌ لا يملك المساعد صلاحية تنفيذ هذا الإجراء"}

            result = action_func(params or {})
            if result.get("success"):
                self._log_action(normalized_action, params or {}, result)

            self.last_action = {
                "type": normalized_action,
                "params": params or {},
                "result": result,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            return result
        except Exception as exc:
            db.session.rollback()
            return {"success": False, "message": f"❌ خطأ في التنفيذ: {exc}", "error": str(exc)}

    # ─────────────────────────────────────────────────────────────────────
    # Generic model helpers
    # ─────────────────────────────────────────────────────────────────────

    def _columns(self, model) -> set[str]:
        return {column.name for column in getattr(model, "__table__", []).columns} if hasattr(model, "__table__") else set()

    def _new_model(self, model, values: Dict[str, Any]):
        columns = self._columns(model)
        filtered = {key: value for key, value in values.items() if key in columns}
        return model(**filtered)

    def _set_if_exists(self, obj, **values) -> None:
        columns = self._columns(obj.__class__)
        for key, value in values.items():
            if key in columns:
                setattr(obj, key, value)

    def _decimal(self, value: Any, default: str = "0") -> Decimal:
        try:
            return Decimal(str(value if value not in (None, "") else default))
        except (InvalidOperation, ValueError, TypeError):
            return Decimal(default)

    def _int(self, value: Any, default: int = 0) -> int:
        try:
            return int(value if value not in (None, "") else default)
        except (ValueError, TypeError):
            return default

    def _clean(self, value: Any) -> Optional[str]:
        if value is None:
            return None
        text = str(value).strip()
        return text or None

    def _amount_value(self, obj) -> Decimal:
        for name in ("amount", "total_amount", "sale_total", "total"):
            if hasattr(obj, name):
                return self._decimal(getattr(obj, name))
        return Decimal("0")

    # ─────────────────────────────────────────────────────────────────────
    # Customers / suppliers / products
    # ─────────────────────────────────────────────────────────────────────

    def add_customer(self, params: Dict[str, Any]) -> Dict[str, Any]:
        try:
            from models import Customer

            name = self._clean(params.get("name"))
            phone = self._clean(params.get("phone"))
            if not name:
                return {"success": False, "message": "❌ الاسم مطلوب"}
            if not phone:
                return {"success": False, "message": "❌ رقم الهاتف مطلوب"}

            existing = Customer.query.filter_by(phone=phone).first()
            if existing:
                return {"success": False, "message": f"❌ العميل موجود مسبقاً (ID: {existing.id})", "existing_customer": {"id": existing.id, "name": existing.name, "phone": existing.phone}}

            customer = self._new_model(
                Customer,
                {
                    "name": name,
                    "phone": phone,
                    "email": self._clean(params.get("email")),
                    "address": self._clean(params.get("address")),
                    "city": self._clean(params.get("city")),
                    "tax_id": self._clean(params.get("tax_id")),
                    "opening_balance": self._decimal(params.get("opening_balance")),
                    "notes": self._clean(params.get("notes")),
                    "is_active": True,
                    "created_by_id": self.user_id,
                    "created_by": self.user_id,
                },
            )
            db.session.add(customer)
            db.session.commit()
            return {"success": True, "message": f"✅ تم إضافة العميل '{customer.name}' بنجاح", "customer_id": customer.id, "data": {"id": customer.id, "name": customer.name, "phone": customer.phone}}
        except Exception as exc:
            db.session.rollback()
            return {"success": False, "message": f"❌ فشل إضافة العميل: {exc}", "error": str(exc)}

    def add_supplier(self, params: Dict[str, Any]) -> Dict[str, Any]:
        try:
            from models import Supplier

            name = self._clean(params.get("name"))
            phone = self._clean(params.get("phone"))
            if not name:
                return {"success": False, "message": "❌ الاسم مطلوب"}
            if not phone:
                return {"success": False, "message": "❌ رقم الهاتف مطلوب"}

            existing = Supplier.query.filter_by(phone=phone).first()
            if existing:
                return {"success": False, "message": f"❌ المورد موجود مسبقاً (ID: {existing.id})"}

            supplier = self._new_model(
                Supplier,
                {
                    "name": name,
                    "phone": phone,
                    "email": self._clean(params.get("email")),
                    "address": self._clean(params.get("address")),
                    "city": self._clean(params.get("city")),
                    "tax_id": self._clean(params.get("tax_id")),
                    "opening_balance": self._decimal(params.get("opening_balance")),
                    "notes": self._clean(params.get("notes")),
                    "is_active": True,
                    "created_by_id": self.user_id,
                    "created_by": self.user_id,
                },
            )
            db.session.add(supplier)
            db.session.commit()
            return {"success": True, "message": f"✅ تم إضافة المورد '{supplier.name}' بنجاح", "supplier_id": supplier.id, "data": {"id": supplier.id, "name": supplier.name, "phone": supplier.phone}}
        except Exception as exc:
            db.session.rollback()
            return {"success": False, "message": f"❌ فشل إضافة المورد: {exc}", "error": str(exc)}

    def add_product(self, params: Dict[str, Any]) -> Dict[str, Any]:
        try:
            from models import Product

            name = self._clean(params.get("name"))
            sku = self._clean(params.get("sku"))
            price = params.get("price", params.get("selling_price"))
            if not name:
                return {"success": False, "message": "❌ اسم المنتج مطلوب"}
            if not sku:
                return {"success": False, "message": "❌ رمز المنتج SKU مطلوب"}
            if price in (None, ""):
                return {"success": False, "message": "❌ السعر مطلوب"}

            existing = Product.query.filter_by(sku=sku).first()
            if existing:
                return {"success": False, "message": f"❌ رمز المنتج موجود مسبقاً (ID: {existing.id})"}

            product = self._new_model(
                Product,
                {
                    "name": name,
                    "sku": sku,
                    "barcode": self._clean(params.get("barcode")),
                    "price": self._decimal(price),
                    "selling_price": self._decimal(price),
                    "cost": self._decimal(params.get("cost", params.get("cost_price"))),
                    "cost_price": self._decimal(params.get("cost", params.get("cost_price"))),
                    "category": self._clean(params.get("category")),
                    "description": self._clean(params.get("description")),
                    "min_stock": self._int(params.get("min_stock")),
                    "max_stock": self._int(params.get("max_stock")),
                    "is_active": True,
                    "created_by_id": self.user_id,
                    "created_by": self.user_id,
                },
            )
            db.session.add(product)
            db.session.commit()
            return {"success": True, "message": f"✅ تم إضافة المنتج '{product.name}' بنجاح", "product_id": product.id, "data": {"id": product.id, "name": product.name, "sku": getattr(product, "sku", None), "price": float(self._amount_value(product))}}
        except Exception as exc:
            db.session.rollback()
            return {"success": False, "message": f"❌ فشل إضافة المنتج: {exc}", "error": str(exc)}

    # ─────────────────────────────────────────────────────────────────────
    # Payments / invoices / sales / expenses / service
    # ─────────────────────────────────────────────────────────────────────

    def create_payment(self, params: Dict[str, Any]) -> Dict[str, Any]:
        try:
            from models import Payment

            amount = params.get("amount", params.get("total_amount"))
            direction = self._clean(params.get("direction"))
            payment_method = self._clean(params.get("payment_method", params.get("method")))
            if amount in (None, ""):
                return {"success": False, "message": "❌ المبلغ مطلوب"}
            if direction not in {"IN", "OUT"}:
                return {"success": False, "message": "❌ الاتجاه يجب أن يكون IN أو OUT"}
            if not payment_method:
                return {"success": False, "message": "❌ طريقة الدفع مطلوبة"}
            if not any(params.get(k) for k in ("customer_id", "supplier_id", "partner_id")):
                return {"success": False, "message": "❌ يجب تحديد عميل أو مورد أو شريك"}

            entity_type = "CUSTOMER" if params.get("customer_id") else "SUPPLIER" if params.get("supplier_id") else "PARTNER"
            payment = self._new_model(
                Payment,
                {
                    "amount": self._decimal(amount),
                    "total_amount": self._decimal(amount),
                    "direction": direction,
                    "method": payment_method,
                    "payment_method": payment_method,
                    "customer_id": params.get("customer_id"),
                    "supplier_id": params.get("supplier_id"),
                    "partner_id": params.get("partner_id"),
                    "notes": self._clean(params.get("notes")),
                    "reference": self._clean(params.get("reference")),
                    "payment_date": datetime.now(timezone.utc),
                    "status": "COMPLETED",
                    "created_by": self.user_id,
                    "created_by_id": self.user_id,
                    "entity_type": entity_type,
                },
            )
            db.session.add(payment)
            db.session.commit()
            saved_amount = self._amount_value(payment)
            return {"success": True, "message": f"✅ تم تسجيل الدفعة بمبلغ {float(saved_amount)} ₪", "payment_id": payment.id, "data": {"id": payment.id, "amount": float(saved_amount), "direction": getattr(payment, "direction", direction), "method": getattr(payment, "method", payment_method)}}
        except Exception as exc:
            db.session.rollback()
            return {"success": False, "message": f"❌ فشل تسجيل الدفعة: {exc}", "error": str(exc)}

    def create_invoice(self, params: Dict[str, Any]) -> Dict[str, Any]:
        try:
            from models import Invoice, InvoiceSource

            invoice_type = self._clean(params.get("invoice_type"))
            total = params.get("total", params.get("total_amount"))
            if not invoice_type:
                return {"success": False, "message": "❌ نوع الفاتورة مطلوب"}
            if total in (None, ""):
                return {"success": False, "message": "❌ الإجمالي مطلوب"}
            if not params.get("customer_id") and not params.get("supplier_id"):
                return {"success": False, "message": "❌ customer_id أو supplier_id مطلوب"}

            source_value = getattr(InvoiceSource.MANUAL, "value", InvoiceSource.MANUAL) if hasattr(InvoiceSource, "MANUAL") else "MANUAL"
            invoice = self._new_model(
                Invoice,
                {
                    "invoice_number": params.get("invoice_number") or f"AI-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
                    "invoice_date": datetime.now(timezone.utc),
                    "customer_id": params.get("customer_id"),
                    "supplier_id": params.get("supplier_id"),
                    "total_amount": self._decimal(total),
                    "amount": self._decimal(total),
                    "notes": self._clean(params.get("notes")),
                    "source": source_value,
                    "created_by_id": self.user_id,
                    "created_by": self.user_id,
                },
            )
            db.session.add(invoice)
            db.session.commit()

            try:
                from models import run_invoice_gl_sync_after_commit
                run_invoice_gl_sync_after_commit(invoice.id)
            except Exception:
                pass

            return {"success": True, "message": f"✅ تم إنشاء الفاتورة بمبلغ {float(self._amount_value(invoice))} ₪", "invoice_id": invoice.id}
        except Exception as exc:
            db.session.rollback()
            return {"success": False, "message": f"❌ فشل إنشاء الفاتورة: {exc}", "error": str(exc)}

    def create_sale(self, params: Dict[str, Any]) -> Dict[str, Any]:
        try:
            from models import Sale, SaleLine

            if not params.get("customer_id"):
                return {"success": False, "message": "❌ معرف العميل مطلوب"}
            if not params.get("warehouse_id"):
                return {"success": False, "message": "❌ معرف المستودع مطلوب"}
            items = params.get("items") or []
            if not items:
                return {"success": False, "message": "❌ يجب إضافة منتج واحد على الأقل"}

            subtotal = Decimal("0")
            lines_data = []
            for item in items:
                if not all(k in item for k in ("product_id", "quantity", "price")):
                    return {"success": False, "message": "❌ بيانات المنتج غير كاملة"}
                quantity = self._decimal(item["quantity"])
                price = self._decimal(item["price"])
                discount = self._decimal(item.get("discount"))
                line_total = (quantity * price) - discount
                subtotal += line_total
                lines_data.append({"product_id": item["product_id"], "quantity": quantity, "price": price, "discount": discount, "total": line_total})

            general_discount = self._decimal(params.get("discount"))
            subtotal_after_discount = subtotal - general_discount
            vat_amount = subtotal_after_discount * Decimal("0.16") if params.get("vat_enabled", True) else Decimal("0")
            total = subtotal_after_discount + vat_amount

            sale = self._new_model(
                Sale,
                {
                    "customer_id": params["customer_id"],
                    "warehouse_id": params["warehouse_id"],
                    "sale_date": datetime.now(timezone.utc),
                    "subtotal": subtotal,
                    "discount": general_discount,
                    "vat_amount": vat_amount,
                    "sale_total": total,
                    "total_amount": total,
                    "total": total,
                    "notes": self._clean(params.get("notes")),
                    "status": "CONFIRMED",
                    "created_by_id": self.user_id,
                    "created_by": self.user_id,
                },
            )
            db.session.add(sale)
            db.session.flush()

            for line_data in lines_data:
                sale_line = self._new_model(
                    SaleLine,
                    {
                        "sale_id": sale.id,
                        "product_id": line_data["product_id"],
                        "quantity": line_data["quantity"],
                        "price": line_data["price"],
                        "unit_price": line_data["price"],
                        "discount": line_data["discount"],
                        "total": line_data["total"],
                        "line_total": line_data["total"],
                    },
                )
                db.session.add(sale_line)
            db.session.commit()
            return {"success": True, "message": f"✅ تم إنشاء عملية البيع بمبلغ {float(total)} ₪", "sale_id": sale.id, "data": {"id": sale.id, "customer_id": getattr(sale, "customer_id", None), "subtotal": float(subtotal), "discount": float(general_discount), "vat": float(vat_amount), "total": float(total), "items_count": len(lines_data)}}
        except Exception as exc:
            db.session.rollback()
            return {"success": False, "message": f"❌ فشل إنشاء البيع: {exc}", "error": str(exc)}

    def create_expense(self, params: Dict[str, Any]) -> Dict[str, Any]:
        try:
            from models import Expense

            amount = params.get("amount", params.get("total_amount"))
            description = self._clean(params.get("description", params.get("notes")))
            if amount in (None, ""):
                return {"success": False, "message": "❌ المبلغ مطلوب"}
            if not description:
                return {"success": False, "message": "❌ الوصف مطلوب"}

            expense = self._new_model(
                Expense,
                {
                    "amount": self._decimal(amount),
                    "total_amount": self._decimal(amount),
                    "description": description,
                    "expense_type": params.get("expense_type", "OTHER"),
                    "payment_method": params.get("payment_method", "CASH"),
                    "method": params.get("payment_method", "CASH"),
                    "date": datetime.now(timezone.utc),
                    "created_at": datetime.now(timezone.utc),
                    "created_by_id": self.user_id,
                    "created_by": self.user_id,
                },
            )
            db.session.add(expense)
            db.session.commit()
            return {"success": True, "message": f"✅ تم تسجيل المصروف بمبلغ {float(self._amount_value(expense))} ₪", "expense_id": expense.id}
        except Exception as exc:
            db.session.rollback()
            return {"success": False, "message": f"❌ فشل تسجيل المصروف: {exc}", "error": str(exc)}

    def create_service(self, params: Dict[str, Any]) -> Dict[str, Any]:
        try:
            from models import ServiceRequest

            if not params.get("customer_id"):
                return {"success": False, "message": "❌ معرف العميل مطلوب"}
            issue_description = self._clean(params.get("issue_description", params.get("description")))
            if not issue_description:
                return {"success": False, "message": "❌ وصف العطل مطلوب"}

            service = self._new_model(
                ServiceRequest,
                {
                    "customer_id": params["customer_id"],
                    "issue_description": issue_description,
                    "description": issue_description,
                    "vehicle_model": self._clean(params.get("vehicle_model")),
                    "vehicle_plate": self._clean(params.get("vehicle_plate")),
                    "status": "pending",
                    "created_by_id": self.user_id,
                    "created_by": self.user_id,
                },
            )
            db.session.add(service)
            db.session.commit()
            return {"success": True, "message": f"✅ تم إنشاء طلب الصيانة رقم {service.id}", "service_id": service.id}
        except Exception as exc:
            db.session.rollback()
            return {"success": False, "message": f"❌ فشل إنشاء طلب الصيانة: {exc}", "error": str(exc)}

    # ─────────────────────────────────────────────────────────────────────
    # Warehouse / stock
    # ─────────────────────────────────────────────────────────────────────

    def add_warehouse(self, params: Dict[str, Any]) -> Dict[str, Any]:
        try:
            from models import Warehouse

            name = self._clean(params.get("name"))
            warehouse_type = self._clean(params.get("warehouse_type", params.get("type")))
            if not name:
                return {"success": False, "message": "❌ اسم المستودع مطلوب"}
            if not warehouse_type:
                return {"success": False, "message": "❌ نوع المستودع مطلوب"}

            warehouse = self._new_model(
                Warehouse,
                {
                    "name": name,
                    "warehouse_type": warehouse_type,
                    "type": warehouse_type,
                    "partner_id": params.get("partner_id"),
                    "supplier_id": params.get("supplier_id"),
                    "is_active": True,
                    "created_by_id": self.user_id,
                    "created_by": self.user_id,
                },
            )
            db.session.add(warehouse)
            db.session.commit()
            return {"success": True, "message": f"✅ تم إضافة المستودع '{warehouse.name}'", "warehouse_id": warehouse.id}
        except Exception as exc:
            db.session.rollback()
            return {"success": False, "message": f"❌ فشل إضافة المستودع: {exc}", "error": str(exc)}

    def transfer_stock(self, params: Dict[str, Any]) -> Dict[str, Any]:
        try:
            from models import StockTransfer

            required = ["product_id", "from_warehouse_id", "to_warehouse_id", "quantity"]
            if not all(params.get(k) for k in required):
                return {"success": False, "message": "❌ بيانات التحويل ناقصة"}

            transfer = self._new_model(
                StockTransfer,
                {
                    "product_id": params["product_id"],
                    "from_warehouse_id": params["from_warehouse_id"],
                    "to_warehouse_id": params["to_warehouse_id"],
                    "quantity": self._int(params["quantity"]),
                    "notes": self._clean(params.get("notes")),
                    "status": "PENDING",
                    "created_by_id": self.user_id,
                    "created_by": self.user_id,
                },
            )
            db.session.add(transfer)
            db.session.commit()
            return {"success": True, "message": "✅ تم إنشاء طلب التحويل", "transfer_id": transfer.id}
        except Exception as exc:
            db.session.rollback()
            return {"success": False, "message": f"❌ فشل تحويل المخزون: {exc}", "error": str(exc)}

    def adjust_stock(self, params: Dict[str, Any]) -> Dict[str, Any]:
        try:
            from models import StockAdjustment, StockLevel

            required = ["product_id", "warehouse_id", "new_quantity", "reason"]
            if not all(params.get(k) for k in required):
                return {"success": False, "message": "❌ بيانات الجرد ناقصة"}

            stock = StockLevel.query.filter_by(product_id=params["product_id"], warehouse_id=params["warehouse_id"]).first()
            old_quantity = self._int(getattr(stock, "quantity", 0)) if stock else 0
            new_quantity = self._int(params["new_quantity"])
            difference = new_quantity - old_quantity

            adjustment = self._new_model(
                StockAdjustment,
                {
                    "product_id": params["product_id"],
                    "warehouse_id": params["warehouse_id"],
                    "old_quantity": old_quantity,
                    "new_quantity": new_quantity,
                    "difference": difference,
                    "reason": self._clean(params.get("reason")),
                    "notes": self._clean(params.get("notes")),
                    "created_by_id": self.user_id,
                    "created_by": self.user_id,
                },
            )
            db.session.add(adjustment)

            if stock:
                self._set_if_exists(stock, quantity=new_quantity)
            else:
                stock = self._new_model(StockLevel, {"product_id": params["product_id"], "warehouse_id": params["warehouse_id"], "quantity": new_quantity})
                db.session.add(stock)

            db.session.commit()
            return {"success": True, "message": f"✅ تم تعديل المخزون من {old_quantity} إلى {new_quantity}", "adjustment_id": adjustment.id, "difference": difference}
        except Exception as exc:
            db.session.rollback()
            return {"success": False, "message": f"❌ فشل تعديل المخزون: {exc}", "error": str(exc)}

    # ─────────────────────────────────────────────────────────────────────
    # Audit
    # ─────────────────────────────────────────────────────────────────────

    def _log_action(self, action_type: str, params: Dict, result: Dict) -> None:
        try:
            entity_id = result.get("customer_id") or result.get("supplier_id") or result.get("product_id") or result.get("sale_id") or result.get("invoice_id") or result.get("payment_id") or result.get("expense_id") or result.get("service_id") or result.get("warehouse_id") or result.get("transfer_id") or result.get("adjustment_id") or result.get("id")
            log = self._new_model(
                AuditLog,
                {
                    "user_id": self.user_id,
                    "action": f"ai_action_{action_type}",
                    "entity_type": action_type.replace("add_", "").replace("create_", ""),
                    "entity_id": entity_id,
                    "details": f"AI executed: {action_type}",
                    "ip_address": "AI_SYSTEM",
                    "user_agent": "AI Assistant",
                },
            )
            db.session.add(log)
            db.session.commit()
        except Exception:
            db.session.rollback()


def parse_user_request(message: str) -> Optional[Tuple[str, Dict[str, Any]]]:
    message = str(message or "")
    message_lower = message.lower()
    if any(word in message_lower for word in ["أضف عميل", "اضف عميل", "إضافة عميل", "add customer"]):
        params: Dict[str, Any] = {}
        name_match = re.search(r"اسمه?\s+([^\s،,]+)", message)
        if name_match:
            params["name"] = name_match.group(1)
        phone_match = re.search(r"(?:هاتفه?|موبايل|phone|رقمه?)\s*[:：]?\s*([\d\-+]+)", message)
        if phone_match:
            params["phone"] = phone_match.group(1)
        if params:
            return "add_customer", params
    return None


__all__ = ["ActionExecutor", "parse_user_request", "SAFE_ACTION_ALIASES"]
