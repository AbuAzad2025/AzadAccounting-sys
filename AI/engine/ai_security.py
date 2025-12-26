"""
AI Security Module - حماية المعلومات السرية
يتحكم في ما يمكن للمساعد الذكي مشاركته حسب دور المستخدم
"""

from flask_login import current_user
from typing import Dict, Any, List
import re
from datetime import datetime, timezone

# المعلومات السرية التي يجب حمايتها
SENSITIVE_KEYWORDS = {
    'passwords': ['password', 'passwd', 'pwd', 'كلمة مرور', 'كلمة السر', 'رمز سري'],
    'api_keys': ['api_key', 'api key', 'secret_key', 'token', 'مفتاح', 'api'],
    'database': ['database_url', 'db_uri', 'connection_string', 'قاعدة البيانات'],
    'security': ['csrf', 'session_key', 'encryption', 'hash', 'salt'],
    'financial_details': ['balance_details', 'رصيد تفصيلي', 'حساب بنكي', 'bank account'],
    'user_data': ['email', 'phone', 'address', 'بريد', 'هاتف', 'عنوان'],
}

# مواضيع حساسة - للمالك فقط
OWNER_ONLY_TOPICS = [
    'api_keys',
    'database',
    'security',
    'system_configuration',
    'backup_locations',
    'encryption_keys',
    'secret_key',
    'groq_api',
]

# معلومات يمكن للمدراء رؤيتها
MANAGER_ALLOWED_TOPICS = [
    'statistics',
    'reports',
    'customers',
    'services',
    'products',
    'invoices',
    'navigation',
    'workflows',
]

def is_owner() -> bool:
    """التحقق من أن المستخدم هو المالك"""
    try:
        if not hasattr(current_user, 'is_authenticated') or not current_user.is_authenticated:
            return False
        
        # PBAC: التحقق من الصلاحية بدلاً من الدور
        if hasattr(current_user, 'has_permission'):
            return current_user.has_permission('access_owner_dashboard')
            
        # Fallback for system accounts
        if hasattr(current_user, 'is_system_account') and current_user.is_system_account:
            return True
            
        return False
    except Exception:
        return False

def is_super_admin() -> bool:
    """التحقق من أن المستخدم لديه صلاحيات عليا"""
    return is_owner()

def is_manager() -> bool:
    """التحقق من أن المستخدم مدير"""
    try:
        if is_owner():
            return True
        
        if not hasattr(current_user, 'is_authenticated') or not current_user.is_authenticated:
            return False
            
        # PBAC: التحقق من صلاحيات إدارية عامة
        if hasattr(current_user, 'has_permission'):
            return (current_user.has_permission('view_reports') or 
                    current_user.has_permission('manage_sales') or
                    current_user.has_permission('manage_users'))
        
        return False
    except Exception:
        return False

def get_user_role_name() -> str:
    """الحصول على توصيف مبسط لمستوى المستخدم"""
    try:
        if is_owner():
            return "Owner"
        if is_manager():
            return "Admin"
        return "User"
    except Exception:
        return "Guest"

def is_sensitive_query(message: str) -> Dict[str, Any]:
    """فحص إذا كان السؤال يطلب معلومات حساسة"""
    message_lower = message.lower()
    
    sensitive_found = []
    for category, keywords in SENSITIVE_KEYWORDS.items():
        for keyword in keywords:
            if keyword in message_lower:
                sensitive_found.append({
                    'category': category,
                    'keyword': keyword
                })
    
    is_sensitive = len(sensitive_found) > 0
    
    # فحص المواضيع المحظورة
    is_owner_only = False
    for topic in OWNER_ONLY_TOPICS:
        if topic.lower().replace('_', ' ') in message_lower:
            is_owner_only = True
            break
    
    return {
        'is_sensitive': is_sensitive,
        'is_owner_only': is_owner_only,
        'found': sensitive_found,
        'requires_owner': is_owner_only,
        'requires_manager': is_sensitive and not is_owner_only
    }

def filter_sensitive_data(data: Dict[str, Any], user_role: str) -> Dict[str, Any]:
    """تصفية البيانات الحساسة حسب دور المستخدم"""
    if is_owner():
        return data  # المالك يرى كل شيء
    
    filtered = {}
    for key, value in data.items():
        key_lower = key.lower()
        
        # حجب المعلومات الحساسة
        is_blocked = False
        for category, keywords in SENSITIVE_KEYWORDS.items():
            if any(k in key_lower for k in keywords):
                is_blocked = True
                break
        
        if is_blocked:
            filtered[key] = "***HIDDEN***"
        else:
            filtered[key] = value
    
    return filtered

def get_security_response(message: str, sensitivity: Dict[str, Any]) -> str:
    """رد أمني عند طلب معلومات حساسة"""
    user_role = get_user_role_name()
    
    if sensitivity['requires_owner'] and not is_owner():
        return f"""🔒 **معلومات محمية**

⚠️ هذه المعلومات متاحة للمالك فقط.

**دورك الحالي:** {user_role}
**المطلوب:** access_owner_dashboard

💡 إذا كنت بحاجة لهذه المعلومات، تواصل مع مالك النظام."""
    
    if sensitivity['is_sensitive'] and not is_manager():
        return f"""🔒 **معلومات حساسة**

⚠️ هذه المعلومات تتطلب صلاحيات إدارية.

**دورك الحالي:** {user_role}
**المطلوب:** صلاحيات إدارية مناسبة (مثل view_reports / manage_users)

💡 لمزيد من المعلومات، تواصل مع المدير."""
    
    return ""

def log_security_event(message: str, sensitivity: Dict[str, Any], response_type: str):
    """تسجيل حدث أمني"""
    try:
        from AI.engine.ai_self_review import log_interaction
        
        log_data = {
            'user': current_user.username if hasattr(current_user, 'username') else 'anonymous',
            'role': get_user_role_name(),
            'query': message[:200],  # أول 200 حرف فقط
            'sensitivity': sensitivity,
            'response_type': response_type,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        # يمكن حفظها في ملف أو قاعدة بيانات

    except Exception as e:
        pass  # خطأ محتمل

def sanitize_response(response: str) -> str:
    """تنظيف الرد من أي معلومات حساسة قد تكون تسربت"""
    if is_owner():
        return response  # المالك يرى كل شيء
    
    # نماذج معلومات حساسة
    patterns = [
        (r'password[:\s]*[^\s]+', 'password: ***'),
        (r'api[_\s]?key[:\s]*[^\s]+', 'api_key: ***'),
        (r'secret[_\s]?key[:\s]*[^\s]+', 'secret_key: ***'),
        (r'token[:\s]*[^\s]+', 'token: ***'),
        (r'sk-[a-zA-Z0-9]+', 'sk-***'),  # OpenAI/Groq keys
        (r'[a-zA-Z0-9]{32,}', '***'),  # hashes طويلة
    ]
    
    sanitized = response
    for pattern, replacement in patterns:
        sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)
    
    return sanitized

