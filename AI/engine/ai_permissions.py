"""
🔐 AI Permissions & Access Control - صلاحيات المساعد الذكي
════════════════════════════════════════════════════════════════════

وظيفة هذا الملف:
- إدارة صلاحيات المساعد الذكي
- التحكم في من يرى المساعد
- صلاحيات تنفيذ العمليات

Created: 2025-11-01
"""

import json
from typing import Dict, List, Any, Optional
from flask_login import current_user
from flask import current_app
from models import SystemSettings


# ═══════════════════════════════════════════════════════════════════════════
# 🎯 AI PERMISSIONS - صلاحيات المساعد
# ═══════════════════════════════════════════════════════════════════════════

AI_CAPABILITIES = {
    "data_access": {
        "read_customers": True,
        "read_suppliers": True,
        "read_products": True,
        "read_sales": True,
        "read_payments": True,
        "read_expenses": True,
        "read_gl": True,
        "read_services": True,
        "read_inventory": True,
        "read_reports": True,
        "read_users": True,  # للمالك فقط
        "read_settings": True,  # للمالك فقط
        "read_audit": True  # للمالك فقط
    },
    
    "data_write": {
        "create_customer": True,
        "create_supplier": True,
        "create_product": True,
        "create_sale": True,
        "create_payment": True,
        "create_expense": True,
        "create_service": True,
        "create_warehouse": True,
        "adjust_stock": True,
        "transfer_stock": True,
        "create_invoice": True
    },
    
    "data_modify": {
        "update_customer": True,
        "update_supplier": True,
        "update_product": True,
        "update_sale": False,  # خطير - ممنوع
        "update_payment": False,  # خطير - ممنوع
        "update_gl": False,  # خطير جداً - ممنوع
        "delete_any": False  # الحذف ممنوع كلياً
    },
    
    "ai_features": {
        "chat": True,
        "realtime_alerts": True,
        "auto_learning": True,
        "suggestions": True,
        "analysis": True,
        "reports": True,
        "predictions": True,
        "training": True  # للمالك فقط
    }
}


def get_ai_permission_setting(key: str, default: Any = None) -> Any:
    """
    الحصول على إعداد صلاحية المساعد
    
    Args:
        key: مفتاح الإعداد (ai_enabled, ai_visible_to_staff, etc.)
        default: القيمة الافتراضية
    
    Returns:
        قيمة الإعداد
    """
    try:
        setting = SystemSettings.query.filter_by(key=key).first()
        
        if setting:
            value = setting.value
            dtype = setting.data_type or 'string'
            if dtype == 'boolean':
                if isinstance(value, str):
                    return value.lower() in ['true', '1', 'yes', 'on']
                return bool(value)
            if dtype in ['integer', 'number']:
                try:
                    return int(value) if dtype == 'integer' else float(value)
                except (TypeError, ValueError):
                    return default
            if dtype == 'json':
                try:
                    return json.loads(value)
                except Exception:
                    return default
            return value
        
        return default
    
    except Exception as e:
        return default


def is_ai_enabled() -> bool:
    """هل المساعد مفعّل في النظام؟"""
    return get_ai_permission_setting('ai_enabled', True)


def is_ai_visible_to_role(role_name: str) -> bool:
    """
    هل المساعد ظاهر لهذا الدور؟
    
    Args:
        role_name: اسم الدور (deprecated - ignored in favor of permissions)
    
    Returns:
        True/False
    """
    # استخدام نظام الصلاحيات الحديث
    if hasattr(current_user, 'is_authenticated') and current_user.is_authenticated:
        # إذا كان لديه صلاحية صريحة
        if hasattr(current_user, 'has_permission') and current_user.has_permission('access_ai_assistant'):
            return True
            
        # المالك دائماً يرى
        if hasattr(current_user, 'has_permission') and current_user.has_permission('access_owner_dashboard'):
            return True

    # Fallback for compatibility if needed, but prefer permissions
    return False


def can_ai_execute_action(action_type: str, user_role: str) -> bool:
    """
    هل المساعد يستطيع تنفيذ هذا الإجراء لهذا المستخدم؟
    يعتمد الآن على الصلاحيات بدلاً من الأدوار الصلبة
    
    Args:
        action_type: نوع الإجراء (add_customer, create_payment, etc.)
        user_role: دور المستخدم (deprecated)
    
    Returns:
        True/False
    """
    if not hasattr(current_user, 'is_authenticated') or not current_user.is_authenticated:
        return False

    # خريطة الصلاحيات المطلوبة لكل إجراء
    ACTION_PERMISSIONS = {
        # Customers
        'add_customer': 'add_customer',
        'create_customer': 'add_customer',
        'update_customer': 'manage_customers',
        'read_customers': 'view_customers',
        
        # Suppliers
        'create_supplier': 'add_supplier',
        'update_supplier': 'manage_vendors',
        'read_suppliers': 'manage_vendors',
        
        # Products & Inventory
        'create_product': 'manage_inventory',
        'update_product': 'manage_inventory',
        'read_products': 'view_parts',
        'adjust_stock': 'manage_inventory',
        'transfer_stock': 'warehouse_transfer',
        'create_warehouse': 'manage_warehouses',
        
        # Sales
        'create_sale': 'manage_sales',
        'create_invoice': 'manage_sales',
        'update_sale': 'manage_sales',
        'read_sales': 'view_sales',
        
        # Service
        'create_service': 'manage_service',
        'read_services': 'view_service',
        
        # Payments & Expenses
        'create_payment': 'manage_payments',
        'update_payment': 'manage_payments',
        'read_payments': 'manage_payments',
        'create_expense': 'manage_expenses',
        'read_expenses': 'manage_expenses',
        'delete_payment': 'manage_payments',
        'delete_split': 'manage_payments',
        'delete_split_ref': 'manage_payments',
        'delete_check': 'manage_payments',
        'delete_expense': 'manage_expenses',
        'delete_sale': 'manage_sales',
        'archive_sale': 'archive_sale',
        'archive_check': 'manage_payments',
        'archive_expense': 'manage_expenses',
        'void_gl_batch': 'manage_ledger',
        'reverse_gl_batch': 'manage_ledger',
        'fix_unbalanced_batches': 'validate_accounting',
        
        # Reports
        'read_reports': 'view_reports',
        
        # System
        'update_gl': 'manage_ledger',
        'read_gl': 'manage_ledger',
        'read_audit': 'view_audit_logs',
        'read_users': 'manage_users',
        'read_settings': 'access_owner_dashboard',
        
        # AI Specific
        'training': 'train_ai',
    }
    
    # تحديد الصلاحية المطلوبة
    required_perm = ACTION_PERMISSIONS.get(action_type)
    
    if required_perm:
        return current_user.has_permission(required_perm)
        
    # إذا لم يكن الإجراء معروفاً، نمنعه افتراضياً للأمان
    return False


def get_ai_access_level(user) -> str:
    """
    الحصول على مستوى الوصول للمساعد
    
    Returns:
        'full' | 'limited' | 'readonly' | 'none'
    """
    if not user or not user.is_authenticated:
        return 'none'
    
    # المالك: وصول كامل
    if user.is_system_account or user.username == '__OWNER__':
        return 'full'
    
    # التحقق باستخدام الصلاحيات بدلاً من الأدوار
    if user.has_permission('manage_ai') or user.has_permission('access_owner_dashboard'):
        return 'full'
    
    # فحص إذا كان المساعد مخفي
    if not is_ai_enabled():
        return 'none'
    
    # التحقق من صلاحية الوصول الأساسية
    if user.has_permission('access_ai_assistant'):
        # تحديد مستوى الوصول بناءً على صلاحيات التعديل
        has_write_access = (
            user.has_permission('manage_sales') or 
            user.has_permission('manage_inventory') or 
            user.has_permission('manage_customers') or
            user.has_permission('manage_service')
        )
        return 'limited' if has_write_access else 'readonly'
    
    return 'none'


__all__ = [
    'AI_CAPABILITIES',
    'get_ai_permission_setting',
    'is_ai_enabled',
    'is_ai_visible_to_role',
    'can_ai_execute_action',
    'get_ai_access_level'
]
