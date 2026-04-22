"""
نظام توثيق المخزون المحسّن - Enhanced Stock Audit System
=========================================================

هذا النظام يضمن:
1. عدم خصم القطعة أكثر من مرة (Idempotent)
2. التوثيق الكامل لكل عملية مع نوعها (صيانة، بيع، حجز، إلخ)
3. التحقق من عدم التكرار عند إعادة الفتح
4. تسجيل المستخدم دائماً
"""

from enum import Enum
from datetime import datetime, timezone
from flask_login import current_user
from flask import request, has_request_context
from extensions import db
from models import AuditLog, StockLevel, ServiceRequest
import json
import hashlib


class StockTransactionType(str, Enum):
    """أنواع عمليات المخزون"""
    # عمليات الصيانة
    SERVICE_CONSUME = "SERVICE_CONSUME"           # خصم عند إكمال صيانة
    SERVICE_RELEASE = "SERVICE_RELEASE"           # إرجاع عند إعادة فتح صيانة
    SERVICE_ADD_PART = "SERVICE_ADD_PART"         # إضافة قطعة للصيانة
    SERVICE_REMOVE_PART = "SERVICE_REMOVE_PART"   # حذف قطعة من الصيانة
    SERVICE_EDIT_PART = "SERVICE_EDIT_PART"       # تعديل قطعة في الصيانة
    
    # عمليات البيع
    SALE_CONSUME = "SALE_CONSUME"                 # خصم عند بيع
    SALE_RETURN = "SALE_RETURN"                   # إرجاع عند مرتجع بيع
    
    # عمليات الحجز
    HOLD_RESERVE = "HOLD_RESERVE"                 # حجز مخزون
    HOLD_RELEASE = "HOLD_RELEASE"                 # إلغاء حجز
    
    # عمليات الشحنات
    SHIPMENT_OUT = "SHIPMENT_OUT"                 # إخراج من الشحنة
    SHIPMENT_RETURN = "SHIPMENT_RETURN"           # إرجاع للشحنة
    
    # عمليات المستودعات
    WAREHOUSE_TRANSFER_OUT = "WAREHOUSE_TRANSFER_OUT"    # تحويل خارج
    WAREHOUSE_TRANSFER_IN = "WAREHOUSE_TRANSFER_IN"      # تحويل وارد
    WAREHOUSE_ADJUSTMENT = "WAREHOUSE_ADJUSTMENT"        # تسوية
    WAREHOUSE_INITIAL = "WAREHOUSE_INITIAL"              # رصيد افتتاحي


class StockAuditLogger:
    """نظام توثيق المخزون المحسّن"""
    
    @staticmethod
    def _generate_transaction_id(service_id: int, part_id: int, warehouse_id: int, 
                                  transaction_type: str, qty: int) -> str:
        """توليد معرف فريد للعملية لمنع التكرار"""
        key = f"{service_id}:{part_id}:{warehouse_id}:{transaction_type}:{qty}"
        return hashlib.md5(key.encode()).hexdigest()[:16]
    
    @staticmethod
    def _check_duplicate_transaction(service_id: int, part_id: int, warehouse_id: int,
                                      transaction_type: str, qty: int) -> bool:
        """التحقق مما إذا كانت العملية مكررة"""
        transaction_id = StockAuditLogger._generate_transaction_id(
            service_id, part_id, warehouse_id, transaction_type, qty
        )
        
        # البحث في آخر 24 ساعة
        from datetime import timedelta
        time_threshold = datetime.now(timezone.utc) - timedelta(hours=24)
        
        existing = db.session.query(AuditLog).filter(
            AuditLog.model_name == "ServiceRequest",
            AuditLog.record_id == service_id,
            AuditLog.action == transaction_type,
            AuditLog.new_data.contains(f'"part_id": {part_id}'),
            AuditLog.new_data.contains(f'"warehouse_id": {warehouse_id}'),
            AuditLog.new_data.contains(f'"qty": {qty}'),
            AuditLog.created_at >= time_threshold
        ).first()
        
        return existing is not None
    
    @staticmethod
    def log_stock_transaction(service, transaction_type, items: list[dict], reason: str = None) -> bool:
        """
        تسجيل عملية مخزون مع التحقق من عدم التكرار
        
        Args:
            service: كائن طلب الصيانة
            transaction_type: نوع العملية (StockTransactionType أو str)
            items: قائمة القطع [{part_id, warehouse_id, qty, stock_after}]
            reason: سبب العملية (اختياري)
        
        Returns:
            bool: True إذا تم التسجيل، False إذا كانت مكررة
        """
        try:
            # التعامل مع نوع العملية (enum أو string)
            if isinstance(transaction_type, StockTransactionType):
                transaction_type_str = transaction_type.value
                transaction_type_name = transaction_type.name
            else:
                transaction_type_str = str(transaction_type)
                transaction_type_name = str(transaction_type)
            # التحقق من كل قطعة - لا نسجل إذا كانت مكررة
            filtered_items = []
            for item in items:
                part_id = item.get('part_id')
                warehouse_id = item.get('warehouse_id')
                qty = item.get('qty')
                
                # التحقق من عدم التكرار
                if StockAuditLogger._check_duplicate_transaction(
                    service.id, part_id, warehouse_id, transaction_type_str, qty
                ):
                    from flask import current_app
                    current_app.logger.info(
                        f"Duplicate transaction skipped: {transaction_type_str} "
                        f"for service {service.id}, part {part_id}"
                    )
                    continue
                
                filtered_items.append(item)
            
            if not filtered_items:
                return False
            
            # إعداد البيانات
            payload = {
                "items": filtered_items,
                "transaction_type": transaction_type_str,
                "reason": reason or transaction_type_name,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "service_status": getattr(service, 'status', None),
                "duplicate_check": True
            }
            
            # الحصول على معلومات المستخدم والطلب
            user_id = None
            ip_address = None
            user_agent = None
            
            try:
                if has_request_context():
                    user_id = current_user.id if current_user and current_user.is_authenticated else None
                    ip_address = request.remote_addr
                    user_agent = request.headers.get("User-Agent", "")
            except RuntimeError:
                pass
            
            # في حالة عدم وجود مستخدم (background tasks)، نستخدم system
            if user_id is None:
                user_id = 1  # system user or admin
            
            # إنشاء سجل التدقيق
            entry = AuditLog(
                created_at=datetime.now(timezone.utc).replace(tzinfo=None),
                model_name="ServiceRequest",
                record_id=service.id,
                customer_id=getattr(service, "customer_id", None),
                user_id=user_id,
                action=transaction_type_str,
                old_data=None,
                new_data=json.dumps(payload, ensure_ascii=False, default=str),
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            db.session.add(entry)
            db.session.flush()
            
            from flask import current_app
            current_app.logger.info(
                f"Stock audit logged: {transaction_type_str} for service {service.id}, "
                f"items: {len(filtered_items)}"
            )
            
            return True
            
        except Exception as e:
            from flask import current_app
            current_app.logger.error(f"Failed to log stock transaction: {e}")
            raise
    
    @staticmethod
    def get_stock_balance(service_id: int, part_id: int = None, warehouse_id: int = None) -> dict:
        """
        الحصول على رصيد المخزون المخصوم لطلب صيانة
        
        Returns:
            dict: { (part_id, warehouse_id): quantity }
        """
        from sqlalchemy import func
        
        query = db.session.query(
            AuditLog.new_data,
            AuditLog.action
        ).filter(
            AuditLog.model_name == "ServiceRequest",
            AuditLog.record_id == service_id,
            AuditLog.action.in_([
                StockTransactionType.SERVICE_CONSUME.value,
                StockTransactionType.SERVICE_RELEASE.value,
                StockTransactionType.SERVICE_ADD_PART.value,
                StockTransactionType.SERVICE_REMOVE_PART.value,
                StockTransactionType.SERVICE_EDIT_PART.value
            ])
        )
        
        if part_id:
            query = query.filter(AuditLog.new_data.contains(f'"part_id": {part_id}'))
        
        logs = query.all()
        
        balances = {}
        for log in logs:
            try:
                data = json.loads(log.new_data or '{}')
                items = data.get('items', [])
                action = log.action
                
                for item in items:
                    key = (item.get('part_id'), item.get('warehouse_id'))
                    qty = item.get('qty', 0)
                    
                    # تحديد إشارة الكمية حسب نوع العملية
                    if action in [StockTransactionType.SERVICE_RELEASE.value, 
                                  StockTransactionType.SERVICE_REMOVE_PART.value]:
                        # هذه عمليات إرجاع (موجبة في المخزون، سالبة في الرصيد المخصوم)
                        qty = -abs(qty)
                    
                    balances[key] = balances.get(key, 0) + qty
                    
            except:
                continue
        
        return balances
    
    @staticmethod
    def verify_no_negative_stock(service_id: int) -> list:
        """
        التحقق من عدم وجود مخزون سالب بعد العمليات
        
        Returns:
            list: قائمة بالمشاكل إن وجدت
        """
        balances = StockAuditLogger.get_stock_balance(service_id)
        issues = []
        
        for (part_id, warehouse_id), consumed_qty in balances.items():
            if consumed_qty < 0:
                # التحقق من المخزون الفعلي
                stock = db.session.query(StockLevel).filter_by(
                    product_id=part_id,
                    warehouse_id=warehouse_id
                ).first()
                
                actual_qty = stock.quantity if stock else 0
                
                if actual_qty < 0:
                    issues.append({
                        'part_id': part_id,
                        'warehouse_id': warehouse_id,
                        'consumed': consumed_qty,
                        'actual_stock': actual_qty,
                        'issue': 'NEGATIVE_STOCK'
                    })
        
        return issues


# دوال مساعدة للصيانة
def log_service_part_add(service, part_id: int, warehouse_id: int, qty: int, 
                         stock_after: int, reason: str = None):
    """تسجيل إضافة قطعة للصيانة"""
    return StockAuditLogger.log_stock_transaction(
        service=service,
        transaction_type=StockTransactionType.SERVICE_ADD_PART,
        items=[{
            'part_id': part_id,
            'warehouse_id': warehouse_id,
            'qty': -qty,  # سالب لأنه خصم
            'stock_after': stock_after
        }],
        reason=reason or "إضافة قطعة للصيانة"
    )


def log_service_part_remove(service, part_id: int, warehouse_id: int, qty: int,
                            stock_after: int, reason: str = None):
    """تسجيل حذف/إرجاع قطعة من الصيانة"""
    return StockAuditLogger.log_stock_transaction(
        service=service,
        transaction_type=StockTransactionType.SERVICE_REMOVE_PART,
        items=[{
            'part_id': part_id,
            'warehouse_id': warehouse_id,
            'qty': qty,  # موجب لأنه إرجاع
            'stock_after': stock_after
        }],
        reason=reason or "إزالة قطعة من الصيانة"
    )


def log_service_complete(service, items: list[dict], reason: str = None):
    """تسجيل إكمال الصيانة وخصم المخزون"""
    return StockAuditLogger.log_stock_transaction(
        service=service,
        transaction_type=StockTransactionType.SERVICE_CONSUME,
        items=items,
        reason=reason or "إكمال الصيانة"
    )


def log_service_reopen(service, items: list[dict], reason: str = None):
    """تسجيل إعادة فتح الصيانة وإرجاع المخزون"""
    return StockAuditLogger.log_stock_transaction(
        service=service,
        transaction_type=StockTransactionType.SERVICE_RELEASE,
        items=items,
        reason=reason or "إعادة فتح الصيانة"
    )
