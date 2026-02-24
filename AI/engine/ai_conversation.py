"""
💬 AI Conversation Manager - مدير المحادثة والذاكرة
════════════════════════════════════════════════════════════════════

وظيفة هذا الملف:
- إدارة الذاكرة التحادثية (Conversation Memory)
- تتبع السياق (Context Tracking)
- إدارة الجلسات (Session Management)
- الرد الذكي المحلي (Local Smart Responses)

Refactored: 2025-11-01
"""

from datetime import datetime
from typing import Dict, List, Any, Optional
import json
import os


# ═══════════════════════════════════════════════════════════════════════════
# 🧠 CONVERSATION MEMORY - الذاكرة التحادثية
# ═══════════════════════════════════════════════════════════════════════════

_conversation_memory = {}


def get_or_create_session_memory(session_id: str) -> Dict[str, Any]:
    """
    الحصول على ذاكرة الجلسة أو إنشاءها
    
    Args:
        session_id: معرف الجلسة (مثل: user_123)
    
    Returns:
        ذاكرة الجلسة مع تاريخ المحادثات
    """
    global _conversation_memory
    
    if session_id not in _conversation_memory:
        _conversation_memory[session_id] = {
            'session_id': session_id,
            'created_at': datetime.now().isoformat(),
            'messages': [],
            'context': {},
            'last_entities': []
        }
        
        # محاولة استرجاع المحادثات السابقة من السجل (إنعاش الذاكرة)
        try:
            if session_id.startswith('user_'):
                try:
                    user_id = int(session_id.split('_')[1])
                    conversations_file = os.path.join('AI', 'data', 'conversations.json')
                    
                    if os.path.exists(conversations_file):
                        with open(conversations_file, 'r', encoding='utf-8') as f:
                            all_convs = json.load(f)
                            
                        # استخراج محادثات المستخدم
                        user_convs = [c for c in all_convs if c.get('user_id') == user_id]
                        
                        # استرجاع آخر 10 تفاعلات
                        for conv in user_convs[-10:]:
                            _conversation_memory[session_id]['messages'].append({
                                'role': 'user',
                                'content': conv.get('query', ''),
                                'timestamp': conv.get('timestamp')
                            })
                            _conversation_memory[session_id]['messages'].append({
                                'role': 'assistant',
                                'content': conv.get('response', ''),
                                'timestamp': conv.get('timestamp')
                            })
                except Exception:
                    pass
        except Exception:
            pass
    
    return _conversation_memory[session_id]


def add_to_memory(session_id: str, role: str, content: str):
    """
    إضافة رسالة للذاكرة
    
    Args:
        session_id: معرف الجلسة
        role: 'user' أو 'assistant'
        content: محتوى الرسالة
    """
    memory = get_or_create_session_memory(session_id)
    
    memory['messages'].append({
        'role': role,
        'content': content,
        'timestamp': datetime.now().isoformat()
    })
    
    # حفظ آخر 50 رسالة فقط (توفير الذاكرة)
    if len(memory['messages']) > 50:
        memory['messages'] = memory['messages'][-50:]


def clear_session_memory(session_id: str):
    """مسح ذاكرة جلسة معينة"""
    global _conversation_memory
    
    if session_id in _conversation_memory:
        del _conversation_memory[session_id]


def get_conversation_context(session_id: str) -> Dict[str, Any]:
    """
    الحصول على سياق المحادثة
    
    Returns:
        {
            'last_topic': 'customers',
            'last_entities': ['customer_123'],
            'message_count': 10
        }
    """
    memory = get_or_create_session_memory(session_id)
    
    return {
        'message_count': len(memory['messages']),
        'last_entities': memory.get('last_entities', []),
        'context': memory.get('context', {})
    }


# ═══════════════════════════════════════════════════════════════════════════
# 🎯 LOCAL SMART RESPONSES - الردود الذكية المحلية
# ═══════════════════════════════════════════════════════════════════════════

def get_local_faq_responses() -> Dict[str, str]:
    """
    الأسئلة الشائعة - ردود فورية محلية بدون AI
    
    هذه الردود سريعة ولا تحتاج Groq API
    """
    return {
        'من أنت': """🤖 أنا المساعد الذكي المحاسبي المحترف في نظام أزاد.

📌 قدراتي:
• قراءة مباشرة من قاعدة البيانات (87 جدول)
• حسابات مالية دقيقة (VAT، ضرائب، عملات)
• معرفة شاملة بدفتر الأستاذ العام (GL)
• تحليل عميق لأي رقم في النظام
• خبير في القانون الضريبي (فلسطين + إسرائيل)

🏢 النظام:
• الشركة: أزاد للأنظمة الذكية
• المطور: المهندس أحمد غنام
• الموقع: رام الله - فلسطين 🇵🇸""",
        
        'ما قدراتك': """🧠 قدراتي الكاملة كمحاسب محترف:

1. 📊 التحليل المحاسبي:
   • شرح أي رقم بالتفصيل (من أين؟ كيف؟ لماذا؟)
   • تتبع المعاملات من البداية للنهاية
   • قراءة القيود المحاسبية (GL Entries)
   • كشف الأخطاء المحاسبية

2. 💰 الحسابات المالية:
   • حساب VAT (16% فلسطين / 17% إسرائيل)
   • حساب ضريبة الدخل
   • تحويل العملات
   • حساب الأرباح والخسائر

3. 📈 القوائم المالية:
   • قائمة الدخل (Income Statement)
   • الميزانية العمومية (Balance Sheet)
   • قائمة التدفقات النقدية
   • ميزان المراجعة (Trial Balance)

4. 🔍 التدقيق المالي:
   • فحص توازن القيود
   • كشف الأخطاء المحاسبية
   • اقتراح التصحيحات

5. 🧭 التنقل:
   • معرفة كل صفحات النظام (197 صفحة)
   • توجيه مباشر للوحدات""",
        
        'كيف أضيف عميل': """📝 إضافة عميل جديد:

1. اذهب إلى: `/customers/add`
2. أدخل البيانات المطلوبة:
   • الاسم
   • رقم الهاتف
   • البريد الإلكتروني (اختياري)
   • العنوان
3. اضغط حفظ

🔗 الرابط المباشر: /customers/add""",
        
        'اشرح رصيد العميل': """📊 **رصيد العميل - الشرح الكامل:**

🧮 **الصيغة:**
الرصيد = (المبيعات + الفواتير + الخدمات) - (الدفعات الواردة IN)

📍 **المعنى:**
• رصيد سالب (-) = 🔴 أحمر = العميل عليه يدفع
• رصيد موجب (+) = 🟢 أخضر = للعميل رصيد عندنا (دفع زيادة)
• رصيد صفر (0) = ⚪ الحساب مسدد بالكامل

💡 **مثال:**
عميل اشترى بـ 1000 ₪ ودفع 600 ₪
الرصيد = (1000) - (600) = -400 ₪
المعنى: العميل لسه عليه 400 ₪

📊 **القيود المحاسبية:**
• عند البيع: مدين AR (يزيد الدين)
• عند الدفع: دائن AR (ينقص الدين)""",
        
        'كيف أحسب الضريبة': """🧾 **حساب ضريبة القيمة المضافة:**

🇵🇸 **فلسطين (16%):**
• إذا السعر بدون ضريبة:
  الضريبة = المبلغ × 0.16
  مثال: 1000 × 0.16 = 160 ₪

• إذا السعر شامل الضريبة:
  الصافي = الإجمالي ÷ 1.16
  مثال: 1160 ÷ 1.16 = 1000 ₪

🇮🇱 **إسرائيل (17%):**
• بدون ضريبة: المبلغ × 0.17
• شامل: الإجمالي ÷ 1.17

📊 **القيد المحاسبي:**
مدين: AR (الإجمالي)
دائن: SALES (الصافي)
دائن: VAT_PAYABLE (الضريبة)""",

        'كيف أعمل نسخة احتياطية': """💾 **النسخ الاحتياطي (Backup):**

1. اذهب إلى: **الإعدادات > النسخ الاحتياطي**
2. اضغط "إنشاء نسخة جديدة"
3. سيتم حفظ ملف `.sql` مضغوط يحتوي على كل البيانات.

💡 **نصيحة:** النظام يقوم بنسخ احتياطي تلقائي يومياً الساعة 3:00 ص.""",

        'شرح الصلاحيات': """🔐 **نظام الصلاحيات:**

• **المالك (Owner):** وصول كامل لكل شيء.
• **المدير (Admin):** إدارة المستخدمين والإعدادات (بدون حذف نهائي).
• **المحاسب (Accountant):** الوصول للمالية، الفواتير، والتقارير.
• **موظف المبيعات:** إنشاء فواتير وعروض أسعار فقط.
• **أمين المستودع:** إدارة المخزون والشحنات فقط.

يمكن تخصيص الصلاحيات من: `/users/roles`""",

        'كيف أضيف مستخدم': """👤 **إضافة موظف/مستخدم جديد:**

1. اذهب إلى: **المستخدمين > إضافة مستخدم**
2. أدخل الاسم وكلمة المرور
3. اختر "الدور" (Role) المناسب (مدير، محاسب، إلخ)
4. اضغط حفظ

🔗 الرابط: `/users/add`"""
    }


def get_local_quick_answers() -> Dict[str, Any]:
    """
    إجابات سريعة لأسئلة شائعة
    
    تُستخدم للرد الفوري بدون الحاجة لـ Groq
    """
    return {
        'greetings': {
            'patterns': ['مرحبا', 'هلا', 'السلام', 'صباح', 'مساء', 'hello', 'hi'],
            'responses': [
                '🤖 مرحباً! أنا المساعد المحاسبي المحترف. كيف أساعدك اليوم؟',
                '👋 أهلاً وسهلاً! أنا هنا لمساعدتك في أي سؤال محاسبي أو مالي.',
                '🌟 حياك الله! اسألني عن أي شيء في النظام.'
            ]
        },
        
        'thanks': {
            'patterns': ['شكرا', 'مشكور', 'thanks', 'thank you'],
            'responses': [
                '😊 العفو! سعيد بخدمتك.',
                '🙏 على الرحب والسعة!',
                '✨ دائماً في الخدمة!'
            ]
        },
        
        'help': {
            'patterns': ['مساعدة', 'help', 'ساعدني'],
            'responses': [
                """🤝 **كيف أساعدك؟**

يمكنني مساعدتك في:
• شرح أي رقم أو رصيد
• حساب الضرائب
• تحليل القيود المحاسبية
• القوائم المالية
• التدقيق المالي
• أي سؤال عن النظام

اسألني أي شيء! 💬"""
            ]
        }
    }


import re
from sqlalchemy import func

# ═══════════════════════════════════════════════════════════════════════════
# ⚡ LOCAL COMMAND ENGINE - محرك الأوامر المحلي
# ═══════════════════════════════════════════════════════════════════════════

def _execute_local_command(message: str, session_id: str = None) -> Optional[str]:
    """
    تنفيذ أوامر مباشرة بناءً على أنماط Regex
    
    المزايا:
    - سرعة فائقة (بدون API)
    - دقة 100% في الأرقام
    - دعم التنقل
    """
    message = message.lower().strip()
    
    # استرجاع الذاكرة إذا وجدت
    memory = get_or_create_session_memory(session_id) if session_id else {}
    last_context = memory.get('context', {})

    # 1. أوامر العد والإحصاء (كم عدد...)
    # ---------------------------------------------------------
    count_patterns = {
        r'عدد العملاء': ('Customer', 'العملاء'),
        r'عدد الموردين': ('Supplier', 'الموردين'),
        r'عدد المستخدمين': ('User', 'المستخدمين'),
        r'عدد المنتجات': ('Product', 'المنتجات'),
        r'عدد الفواتير': ('Invoice', 'الفواتير'),
    }
    
    for pattern, (model_name, label) in count_patterns.items():
        if re.search(pattern, message):
            try:
                from extensions import db
                # Lazy import models
                import models
                Model = getattr(models, model_name, None)
                
                if Model:
                    count = db.session.query(func.count(Model.id)).scalar()
                    return f"📊 **إحصائيات النظام:**\n\nعدد {label} المسجلين حالياً: **{count}**"
            except Exception:
                pass

    # 2. أسعار العملات (سعر صرف...)
    # ---------------------------------------------------------
    currency_match = re.search(r'سعر (صرف )?(\w+)', message)
    if currency_match:
        currency_name = currency_match.group(2)
        # خريطة العملات الشائعة
        currency_map = {
            'دولار': 'USD', 'الدولار': 'USD', 'usd': 'USD',
            'يورو': 'EUR', 'اليورو': 'EUR', 'eur': 'EUR',
            'دينار': 'JOD', 'الدينار': 'JOD', 'jod': 'JOD',
            'شيكل': 'ILS', 'الشيكل': 'ILS', 'ils': 'ILS'
        }
        
        code = currency_map.get(currency_name)
        if code:
            try:
                from models import fx_rate
                rate = fx_rate(code, 'ILS')  # السعر مقابل الشيكل افتراضياً
                return f"💱 **سعر الصرف الحالي:**\n\n1 {code} = **{rate:.2f}** ILS\n(السعر تقريبي وقد يختلف حسب المصدر)"
            except Exception:
                pass

    # 3. التنقل السريع (اذهب إلى...)
    # ---------------------------------------------------------
    nav_patterns = {
        r'(اذهب|انتقل|افتح).*العملاء': '/customers',
        r'(اذهب|انتقل|افتح).*الموردين': '/vendors/suppliers',
        r'(اذهب|انتقل|افتح).*الفواتير': '/sales',
        r'(اذهب|انتقل|افتح).*المخزون': '/warehouses',
        r'(اذهب|انتقل|افتح).*التقارير': '/reports',
        r'(اذهب|انتقل|افتح).*الإعدادات': '/settings', # افتراضي
        r'(اذهب|انتقل|افتح).*المستخدمين': '/users',
    }
    
    for pattern, url in nav_patterns.items():
        if re.search(pattern, message):
            return f"""🚀 **تنقل سريع:**
            
يمكنك الذهاب مباشرة عبر هذا الرابط:
[{url}]({url})"""

    # 4. مبيعات اليوم (بسيط)
    # ---------------------------------------------------------
    if re.search(r'مبيعات اليوم', message):
        try:
            from extensions import db
            from models import Sale
            from datetime import date
            
            today = date.today()
            total = db.session.query(func.sum(Sale.total_amount))\
                .filter(func.date(Sale.sale_date) == today)\
                .scalar() or 0
            
            return f"💰 **مبيعات اليوم:**\n\nإجمالي المبيعات المسجلة اليوم: **{total:.2f}**"
        except Exception:
            pass

    # 5. تحليل عميل (Deep Accounting)
    # ---------------------------------------------------------
    customer_match = re.search(r'(تحليل|رصيد|وضع) عميل (.+)', message)
    # 5.1. أو استكمال سياق (رصيده، كشف حسابه...)
    context_match = re.search(r'(رصيده|حسابه|كشفه|وضعه)', message)
    
    target_customer_name = None
    
    if customer_match:
        target_customer_name = customer_match.group(2).strip()
    elif context_match and last_context.get('last_customer_id'):
        # استخدام السياق السابق
        try:
            from models import Customer
            c = Customer.query.get(last_context['last_customer_id'])
            if c:
                target_customer_name = c.name
        except:
            pass

    if target_customer_name:
        try:
            from models import Customer, Sale, Invoice
            from extensions import db
            
            # البحث عن العميل
            customer = Customer.query.filter(Customer.name.ilike(f'%{target_customer_name}%')).first()
            
            if customer:
                # 🧠 تحديث الذاكرة والسياق
                if session_id:
                    memory['context']['last_customer_id'] = customer.id
                    memory['context']['last_topic'] = 'customer_analysis'
                
                # حساب الرصيد
                balance = customer.account_balance
                balance_color = "text-danger" if balance < 0 else "text-success"
                balance_text = "عليه" if balance < 0 else "له"
                
                # آخر 3 فواتير
                last_invoices = Invoice.query.filter_by(customer_id=customer.id)\
                    .order_by(Invoice.date.desc()).limit(3).all()
                
                invoices_html = ""
                for inv in last_invoices:
                    status_badge = f'<span class="badge bg-{"success" if inv.is_paid else "warning"}">{inv.status}</span>'
                    invoices_html += f"""
                    <tr>
                        <td>#{inv.invoice_number}</td>
                        <td>{inv.date.strftime('%Y-%m-%d')}</td>
                        <td>{inv.total_amount:.2f}</td>
                        <td>{status_badge}</td>
                    </tr>
                    """
                
                if not invoices_html:
                    invoices_html = "<tr><td colspan='4' class='text-center text-muted'>لا توجد فواتير حديثة</td></tr>"

                return f"""
                <div class="card shadow-sm border-0">
                    <div class="card-header bg-light d-flex justify-content-between align-items-center">
                        <h6 class="mb-0"><i class="fas fa-user-tie text-primary"></i> {customer.name}</h6>
                        <span class="badge bg-info">{customer.customer_type}</span>
                    </div>
                    <div class="card-body">
                        <div class="row text-center mb-3">
                            <div class="col-6">
                                <small class="text-muted">الرصيد الحالي</small>
                                <h4 class="{balance_color} mb-0">{abs(balance):.2f} {customer.currency or 'ILS'}</h4>
                                <small class="{balance_color}">{balance_text}</small>
                            </div>
                            <div class="col-6">
                                <small class="text-muted">رقم الهاتف</small>
                                <p class="mb-0">{customer.phone or 'غير مسجل'}</p>
                            </div>
                        </div>
                        
                        <h6 class="small text-muted mb-2">📄 آخر الفواتير:</h6>
                        <div class="table-responsive">
                            <table class="table table-sm table-hover" style="font-size: 0.85rem;">
                                <thead>
                                    <tr>
                                        <th>رقم</th>
                                        <th>تاريخ</th>
                                        <th>مبلغ</th>
                                        <th>حالة</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {invoices_html}
                                </tbody>
                            </table>
                        </div>
                        
                        <div class="d-grid gap-2 mt-3">
                            <a href="/sales/new?customer={customer.id}" class="btn btn-sm btn-primary">
                                <i class="fas fa-plus"></i> فاتورة جديدة
                            </a>
                            <a href="/customers/{customer.id}" class="btn btn-sm btn-outline-secondary">
                                <i class="fas fa-external-link-alt"></i> ملف العميل الكامل
                            </a>
                        </div>
                    </div>
                </div>
                """
            else:
                return f"❌ عذراً، لم أجد عميلاً بهذا الاسم: **{target_customer_name}**"
        except Exception as e:
            return f"⚠️ حدث خطأ أثناء تحليل العميل: {str(e)}"

    # 6. الوضع المالي (Financial Snapshot)
    # ---------------------------------------------------------
    if re.search(r'(وضع مالي|كيف الشغل|ملخص مالي)', message):
        try:
            from extensions import db
            from models import Sale, Expense
            from datetime import date, timedelta
            
            today = date.today()
            month_start = today.replace(day=1)
            
            # مبيعات اليوم والشهر
            sales_today = db.session.query(func.sum(Sale.total_amount)).filter(func.date(Sale.sale_date) == today).scalar() or 0
            sales_month = db.session.query(func.sum(Sale.total_amount)).filter(Sale.sale_date >= month_start).scalar() or 0
            
            # مصروفات اليوم والشهر
            exp_today = db.session.query(func.sum(Expense.amount)).filter(func.date(Expense.date) == today).scalar() or 0
            exp_month = db.session.query(func.sum(Expense.amount)).filter(Expense.date >= month_start).scalar() or 0
            
            # صافي الربح التقديري
            net_today = sales_today - exp_today
            net_month = sales_month - exp_month
            
            return f"""
            <div class="card shadow-sm border-0 bg-gradient-primary text-white">
                <div class="card-body p-3">
                    <h5 class="card-title mb-4"><i class="fas fa-chart-pie"></i> الملخص المالي</h5>
                    
                    <div class="row g-2 mb-3">
                        <div class="col-6">
                            <div class="p-2 bg-white bg-opacity-25 rounded">
                                <small>مبيعات اليوم</small>
                                <h5 class="mb-0">{sales_today:.2f}</h5>
                            </div>
                        </div>
                        <div class="col-6">
                            <div class="p-2 bg-white bg-opacity-25 rounded">
                                <small>مصروفات اليوم</small>
                                <h5 class="mb-0 text-warning">{exp_today:.2f}</h5>
                            </div>
                        </div>
                    </div>
                    
                    <div class="border-top border-light pt-2 mt-2">
                        <div class="d-flex justify-content-between align-items-center">
                            <span>صافي ربح الشهر:</span>
                            <span class="h4 mb-0 { 'text-warning' if net_month < 0 else '' }">{net_month:.2f}</span>
                        </div>
                        <small class="opacity-75">المبيعات ({sales_month}) - المصروفات ({exp_month})</small>
                    </div>
                    
                    <div class="mt-3 text-center">
                        <a href="/reports/financial" class="btn btn-sm btn-light text-primary w-100">
                            <i class="fas fa-file-invoice-dollar"></i> التقرير المالي المفصل
                        </a>
                    </div>
                </div>
            </div>
            """
        except Exception as e:
            return f"⚠️ حدث خطأ في جلب البيانات المالية: {str(e)}"

    return None


def match_local_response(message: str, session_id: str = None) -> Optional[str]:
    """
    محاولة إيجاد رد محلي سريع
    
    Args:
        message: رسالة المستخدم
        session_id: معرف الجلسة
    
    Returns:
        الرد المحلي أو None
    """
    message_lower = message.lower().strip()
    
    # 0.⚡ محاولة تنفيذ أمر محلي (جديد)
    command_response = _execute_local_command(message, session_id=session_id)
    if command_response:
        return command_response
    
    # 1. الأسئلة الشائعة (FAQ)
    faqs = get_local_faq_responses()
    for question, answer in faqs.items():
        if question.lower() in message_lower:
            return answer
    
    # 2. الردود السريعة
    quick = get_local_quick_answers()
    
    import random
    
    for category, data in quick.items():
        patterns = data['patterns']
        for pattern in patterns:
            if pattern in message_lower:
                return random.choice(data['responses'])
    
    return None


# ═══════════════════════════════════════════════════════════════════════════
# 📊 CONVERSATION ANALYTICS - تحليلات المحادثة
# ═══════════════════════════════════════════════════════════════════════════

def get_conversation_stats() -> Dict[str, Any]:
    """إحصائيات المحادثات"""
    global _conversation_memory
    
    total_sessions = len(_conversation_memory)
    total_messages = sum(
        len(session['messages'])
        for session in _conversation_memory.values()
    )
    
    return {
        'total_sessions': total_sessions,
        'total_messages': total_messages,
        'active_sessions': total_sessions
    }


__all__ = [
    'get_or_create_session_memory',
    'add_to_memory',
    'clear_session_memory',
    'get_conversation_context',
    'get_local_faq_responses',
    'match_local_response',
    'get_conversation_stats'
]

