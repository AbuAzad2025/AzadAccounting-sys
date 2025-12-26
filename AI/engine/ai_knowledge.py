

import os
import re
import json
from pathlib import Path
from datetime import datetime

KNOWLEDGE_CACHE_FILE = 'AI/data/ai_knowledge_cache.json'
TRAINING_LOG_FILE = 'AI/data/ai_training_log.json'

class SystemKnowledgeBase:
    
    def __init__(self):
        self.base_path = Path('.')
        self.knowledge = {
            'models': {},
            'enums': {},
            'routes': {},
            'templates': {},
            'forms': {},
            'functions': {},
            'javascript': {},
            'css': {},
            'static_files': {},
            'relationships': {},
            'business_rules': [],
            'common_errors': [],
            'last_indexed': None,
            'index_count': 0
        }
        self.load_from_cache()
    
    def load_from_cache(self):
        try:
            if os.path.exists(KNOWLEDGE_CACHE_FILE):
                with open(KNOWLEDGE_CACHE_FILE, 'r', encoding='utf-8') as f:
                    cached = json.load(f)
                    self.knowledge.update(cached)

        except Exception as e:
            pass
    
    def save_to_cache(self):
        """حفظ المعرفة في الذاكرة المستمرة"""
        try:
            os.makedirs('AI/data', exist_ok=True)
            self.knowledge['last_indexed'] = datetime.now().isoformat()
            self.knowledge['index_count'] = self.knowledge.get('index_count', 0) + 1
            
            with open(KNOWLEDGE_CACHE_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.knowledge, f, ensure_ascii=False, indent=2)

        except Exception as e:
            pass
    
    def index_all_files(self, force_reindex=False):
        """فهرسة كل ملفات النظام مع حفظ مستمر - شاملة 100%"""
        if not force_reindex and self.knowledge.get('last_indexed'):
            return self.knowledge
        
        
        self.index_models()
        self.index_forms()
        self.index_routes()
        self.index_all_functions()
        self.index_templates()
        self.index_javascript()
        self.index_css()
        self.index_static_files()
        self.analyze_relationships()
        self.extract_business_rules()
        self.extract_currency_rules()
        
        self.save_to_cache()
        
        total_items = (
            len(self.knowledge['models']) +
            len(self.knowledge.get('enums', {})) +
            len(self.knowledge['forms']) +
            len(self.knowledge['routes']) +
            len(self.knowledge['functions']) +
            len(self.knowledge['templates']) +
            len(self.knowledge['javascript']) +
            len(self.knowledge['css'])
        )

        # حساب جودة التعلم (Learning Quality Index)
        self.calculate_learning_quality()
        
        return self.knowledge
    
    def calculate_learning_quality(self):
        """حساب مؤشر جودة التعلم (Learning Quality Index)"""
        try:
            # 1. نسبة الجداول التي تحتوي بيانات
            from models import (
                Customer, Supplier, Product, ServiceRequest, Invoice, 
                Payment, Expense, Warehouse, User
            )
            
            tables_with_data = 0
            total_critical_tables = 8
            
            if Customer.query.count() > 0: tables_with_data += 1
            if Supplier.query.count() > 0: tables_with_data += 1
            if Product.query.count() > 0: tables_with_data += 1
            if ServiceRequest.query.count() > 0: tables_with_data += 1
            if Invoice.query.count() > 0: tables_with_data += 1
            if Payment.query.count() > 0: tables_with_data += 1
            if Expense.query.count() > 0: tables_with_data += 1
            if Warehouse.query.count() > 0: tables_with_data += 1
            
            data_density_score = (tables_with_data / total_critical_tables) * 100
            
            # 2. نسبة المكونات المفهرسة
            total_indexed = (
                len(self.knowledge.get('models', {})) +
                len(self.knowledge.get('routes', {})) +
                len(self.knowledge.get('templates', {}))
            )
            
            system_health_score = min(100, (total_indexed / 10))  # كل 10 عناصر = 1%
            
            # 3. متوسط الثقة (من ai_interactions.json)
            avg_confidence = 75  # افتراضي
            try:
                import json
                if os.path.exists('AI/data/ai_interactions.json'):
                    with open('AI/data/ai_interactions.json', 'r', encoding='utf-8') as f:
                        interactions = json.load(f)
                        if interactions:
                            recent = interactions[-20:]
                            avg_confidence = sum(i.get('confidence', 0) for i in recent) / len(recent)
            except Exception:
                pass
            
            # حساب المؤشر النهائي
            learning_quality = (avg_confidence + data_density_score + system_health_score) / 3
            
            self.knowledge['learning_quality'] = {
                'index': round(learning_quality, 2),
                'avg_confidence': round(avg_confidence, 2),
                'data_density': round(data_density_score, 2),
                'system_health': round(system_health_score, 2),
                'tables_with_data': tables_with_data,
                'total_critical_tables': total_critical_tables
            }

        except Exception as e:
            pass  # خطأ محتمل
    
    def extract_currency_rules(self):
        """استخراج قواعد العملات وسعر الصرف"""
        currency_rules = [
            {
                'rule': 'العملات المدعومة: ILS, USD, JOD, EUR',
                'source': 'models.py - CURRENCY_CHOICES',
                'impact': 'high'
            },
            {
                'rule': 'سعر الصرف يُحفظ مع كل عملية (fx_rate_used)',
                'source': 'models.py - Payment, Invoice',
                'impact': 'high'
            },
            {
                'rule': 'التحويل التلقائي بين العملات عند الدفع',
                'source': 'routes/payments.py',
                'impact': 'medium'
            },
            {
                'rule': 'سعر الصرف من 3 مصادر: online, manual, default',
                'source': 'models.py - fx_rate_source',
                'impact': 'medium'
            }
        ]
        
        self.knowledge['business_rules'].extend(currency_rules)
    
    def index_models(self):
        """فهرسة Models - فهم الجداول - محسّن لاكتشاف كل النماذج"""
        try:
            models_file = self.base_path / 'models.py'
            if not models_file.exists():
                return
            
            content = models_file.read_text(encoding='utf-8')
            
            # اكتشاف كل الـ classes
            class_pattern = r'^class\s+(\w+)\s*\([^)]*\):'
            all_classes = re.findall(class_pattern, content, re.MULTILINE)
            
            db_models_count = 0
            enums_count = 0
            
            for class_name in all_classes:
                # الحصول على تعريف الـ class
                class_def_pattern = rf'^class\s+{re.escape(class_name)}\s*\(([^)]+)\):'
                class_def = re.search(class_def_pattern, content, re.MULTILINE)
                
                if not class_def:
                    continue
                
                inheritance = class_def.group(1)
                
                # تحديد نوع الـ class
                is_enum = 'enum.Enum' in inheritance or 'str, enum' in inheritance
                is_db_model = 'db.Model' in inheritance
                is_mixin = 'Mixin' in class_name
                
                if is_mixin:
                    continue  # تخطي الـ Mixins
                
                # استخراج الجسم
                class_body_pattern = rf'class\s+{re.escape(class_name)}\s*\([^)]+\):(.*?)(?=\nclass\s+\w+\s*\(|\Z)'
                class_body_match = re.search(class_body_pattern, content, re.DOTALL | re.MULTILINE)
                
                class_body = class_body_match.group(1) if class_body_match else ''
                
                if is_enum:
                    # Enum
                    values = re.findall(r'(\w+)\s*=\s*["\']([^"\']+)["\']', class_body[:1000])
                    self.knowledge['models'][class_name] = {
                        'type': 'enum',
                        'values': [v[0] for v in values[:10]],
                        'file': 'models.py'
                    }
                    enums_count += 1
                
                elif is_db_model:
                    # DB Model
                    columns = re.findall(r'(\w+)\s*=\s*db\.Column\(', class_body)
                    relationships = re.findall(r'(\w+)\s*=\s*db\.relationship\(["\'](\w+)["\']', class_body)
                    
                    self.knowledge['models'][class_name] = {
                        'type': 'db_model',
                        'columns': columns[:50],  # أول 50 عمود
                        'relationships': [rel[1] for rel in relationships],
                        'file': 'models.py',
                        'has_timestamp': 'TimestampMixin' in inheritance,
                        'has_audit': 'AuditMixin' in inheritance,
                    }
                    db_models_count += 1
            
            
        except Exception as e:
            pass  # خطأ محتمل
    
    def index_routes(self):
        """فهرسة Routes - فهم المسارات"""
        try:
            routes_dir = self.base_path / 'routes'
            if not routes_dir.exists():
                return
            
            for route_file in routes_dir.glob('*.py'):
                if route_file.name.startswith('__'):
                    continue
                
                content = route_file.read_text(encoding='utf-8')
                
                route_pattern = r'@\w+_bp\.route\([\'"](.+?)[\'"]\s*,?\s*methods=\[(.+?)\]\)'
                routes = re.findall(route_pattern, content)
                
                blueprint_name = route_file.stem
                
                if routes:
                    self.knowledge['routes'][blueprint_name] = {
                        'file': str(route_file),
                        'routes': [(r[0], r[1]) for r in routes]
                    }
            
            
        except Exception as e:
            pass  # خطأ محتمل
    
    def index_forms(self):
        """فهرسة Forms من forms.py"""
        try:
            forms_file = self.base_path / 'forms.py'
            if not forms_file.exists():
                return
            
            content = forms_file.read_text(encoding='utf-8')
            
            # اكتشاف كل الـ Forms
            form_pattern = r'^class\s+(\w+Form)\s*\('
            forms = re.findall(form_pattern, content, re.MULTILINE)
            
            for form_name in forms:
                # استخراج الحقول
                form_body_pattern = rf'class\s+{re.escape(form_name)}.*?:(.*?)(?=\nclass\s|\Z)'
                form_body = re.search(form_body_pattern, content, re.DOTALL)
                
                if form_body:
                    fields = re.findall(r'(\w+)\s*=\s*(?:StringField|IntegerField|SelectField|TextAreaField|BooleanField|PasswordField|FileField|DateField)', form_body.group(1))
                    
                    self.knowledge['forms'][form_name] = {
                        'fields': fields[:30],
                        'file': 'forms.py'
                    }
            
        
        except Exception as e:
            pass  # خطأ محتمل
    
    def index_all_functions(self):
        """فهرسة جميع الدوال في كل ملفات Python"""
        try:
            function_count = 0
            
            # فهرسة دوال routes/
            routes_dir = self.base_path / 'routes'
            if routes_dir.exists():
                for py_file in routes_dir.glob('*.py'):
                    if py_file.name.startswith('__'):
                        continue
                    
                    content = py_file.read_text(encoding='utf-8')
                    
                    # اكتشاف كل الدوال
                    func_pattern = r'^def\s+(\w+)\s*\('
                    functions = re.findall(func_pattern, content, re.MULTILINE)
                    
                    module_name = f"routes.{py_file.stem}"
                    self.knowledge['functions'][module_name] = functions[:100]
                    function_count += len(functions)
            
            # فهرسة دوال services/
            services_dir = self.base_path / 'services'
            if services_dir.exists():
                for py_file in services_dir.glob('*.py'):
                    if py_file.name.startswith('__'):
                        continue
                    
                    content = py_file.read_text(encoding='utf-8')
                    func_pattern = r'^def\s+(\w+)\s*\('
                    functions = re.findall(func_pattern, content, re.MULTILINE)
                    
                    module_name = f"services.{py_file.stem}"
                    self.knowledge['functions'][module_name] = functions[:100]
                    function_count += len(functions)
            
            # فهرسة الملفات الرئيسية
            for main_file in ['app.py', 'utils.py', 'validators.py', 'acl.py']:
                main_path = self.base_path / main_file
                if main_path.exists():
                    content = main_path.read_text(encoding='utf-8')
                    func_pattern = r'^def\s+(\w+)\s*\('
                    functions = re.findall(func_pattern, content, re.MULTILINE)
                    
                    self.knowledge['functions'][main_file] = functions[:100]
                    function_count += len(functions)

        except Exception as e:
            pass  # خطأ محتمل
    
    def index_javascript(self):
        """فهرسة ملفات JavaScript"""
        try:
            js_dir = self.base_path / 'static' / 'js'
            if not js_dir.exists():
                return
            
            for js_file in js_dir.glob('*.js'):
                content = js_file.read_text(encoding='utf-8')
                
                # اكتشاف الدوال
                func_pattern = r'(?:function\s+(\w+)|const\s+(\w+)\s*=\s*(?:async\s*)?\()'
                functions = re.findall(func_pattern, content)
                functions_names = [f[0] or f[1] for f in functions if f[0] or f[1]]
                
                # اكتشاف event listeners
                events = re.findall(r'addEventListener\(["\'](\w+)["\']', content)
                
                self.knowledge['javascript'][js_file.name] = {
                    'functions': functions_names[:50],
                    'events': list(set(events))[:20],
                    'file': str(js_file.relative_to(self.base_path))
                }
            
        
        except Exception as e:
            pass  # خطأ محتمل
    
    def index_css(self):
        """فهرسة ملفات CSS"""
        try:
            css_dir = self.base_path / 'static' / 'css'
            if not css_dir.exists():
                return
            
            for css_file in css_dir.glob('*.css'):
                content = css_file.read_text(encoding='utf-8')
                
                # اكتشاف الـ classes
                css_classes = re.findall(r'\.([a-zA-Z][\w-]*)\s*\{', content)
                
                # اكتشاف الـ IDs
                css_ids = re.findall(r'#([a-zA-Z][\w-]*)\s*\{', content)
                
                self.knowledge['css'][css_file.name] = {
                    'classes': list(set(css_classes))[:100],
                    'ids': list(set(css_ids))[:50],
                    'file': str(css_file.relative_to(self.base_path))
                }
            
        
        except Exception as e:
            pass  # خطأ محتمل
    
    def index_static_files(self):
        """فهرسة الملفات الثابتة (صور، خطوط، إلخ)"""
        try:
            static_dir = self.base_path / 'static'
            if not static_dir.exists():
                return
            
            file_types = {
                'images': ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.ico'],
                'fonts': ['.ttf', '.woff', '.woff2', '.eot'],
                'data': ['.json', '.xml', '.csv'],
                'other': []
            }
            
            for category in file_types:
                file_types[category] = []
            
            for file_path in static_dir.rglob('*'):
                if file_path.is_file() and not file_path.name.startswith('.'):
                    ext = file_path.suffix.lower()
                    
                    categorized = False
                    for category, extensions in file_types.items():
                        if category == 'other':
                            continue
                        if ext in ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.ico'] and category == 'images':
                            file_types['images'].append(str(file_path.relative_to(static_dir)))
                            categorized = True
                            break
                        elif ext in ['.ttf', '.woff', '.woff2', '.eot'] and category == 'fonts':
                            file_types['fonts'].append(str(file_path.relative_to(static_dir)))
                            categorized = True
                            break
                        elif ext in ['.json', '.xml', '.csv'] and category == 'data':
                            file_types['data'].append(str(file_path.relative_to(static_dir)))
                            categorized = True
                            break
                    
                    if not categorized and ext not in ['.js', '.css']:
                        file_types['other'].append(str(file_path.relative_to(static_dir)))
            
            self.knowledge['static_files'] = {
                'images': file_types['images'][:50],
                'fonts': file_types['fonts'],
                'data': file_types['data'],
                'images_count': len(file_types['images']),
                'fonts_count': len(file_types['fonts']),
                'data_count': len(file_types['data']),
            }
            
            total_static = len(file_types['images']) + len(file_types['fonts']) + len(file_types['data'])

        except Exception as e:
            pass  # خطأ محتمل
    
    def index_templates(self):
        """فهرسة Templates - فهم الواجهات"""
        try:
            templates_dir = self.base_path / 'templates'
            if not templates_dir.exists():
                return
            
            template_count = 0
            for template_file in templates_dir.rglob('*.html'):
                module_name = template_file.parent.name
                if module_name not in self.knowledge['templates']:
                    self.knowledge['templates'][module_name] = []
                
                self.knowledge['templates'][module_name].append(template_file.name)
                template_count += 1

        except Exception as e:
            pass  # خطأ محتمل
    
    def analyze_relationships(self):
        """تحليل العلاقات بين الجداول"""
        for model_name, model_data in self.knowledge['models'].items():
            relationships = model_data.get('relationships', [])
            
            for rel in relationships:
                rel_key = f"{model_name} → {rel}"
                self.knowledge['relationships'][rel_key] = {
                    'from': model_name,
                    'to': rel,
                    'type': 'one-to-many'  # يمكن تحسينها
                }
        
    
    def extract_business_rules(self):
        """استخراج القواعد التشغيلية من الكود"""
        business_rules = [
            {
                'rule': 'كل كراج له قاعدة بيانات مستقلة',
                'source': 'app.py - multi-tenant architecture',
                'impact': 'high'
            },
            {
                'rule': 'لا يمكن حذف دفعة مربوطة بفاتورة',
                'source': 'routes/payments.py',
                'impact': 'high'
            },
            {
                'rule': 'الشريك يتسلم أرباحه بعد التسوية فقط',
                'source': 'models.py - PartnerSettlement',
                'impact': 'medium'
            },
            {
                'rule': 'حساب النظام (ID=1) يتجاوز وضع الصيانة',
                'source': 'app.py - check_maintenance_mode',
                'impact': 'high'
            },
            {
                'rule': 'المخازن بأنواع: Online, Partner, Inventory, Exchange, Main',
                'source': 'models.py - Warehouse',
                'impact': 'medium'
            }
        ]
        
        self.knowledge['business_rules'] = business_rules
    
    def get_accounting_knowledge(self):
        """المعرفة المحاسبية الشاملة - النظام يعرف كل شيء عن المحاسبة"""
        return {
            'gl_accounts': {
                '1100_AR': {'name': 'حساب العملاء (Accounts Receivable)', 'type': 'ASSET', 'arabic': 'ذمم مدينة'},
                '2000_AP': {'name': 'حساب الموردين (Accounts Payable)', 'type': 'LIABILITY', 'arabic': 'ذمم دائنة'},
                '4000_SALES': {'name': 'المبيعات (Sales Revenue)', 'type': 'REVENUE', 'arabic': 'إيرادات المبيعات'},
                '1000_CASH': {'name': 'النقدية (Cash on Hand)', 'type': 'ASSET', 'arabic': 'الصندوق'},
                '1010_BANK': {'name': 'البنك (Bank)', 'type': 'ASSET', 'arabic': 'البنك'},
                '1020_CARD_CLEARING': {'name': 'بطاقات الائتمان (Card Clearing)', 'type': 'ASSET', 'arabic': 'بطاقات'},
                '2100_VAT_PAYABLE': {'name': 'ضريبة القيمة المضافة (VAT Payable)', 'type': 'LIABILITY', 'arabic': 'ضريبة المضافة'},
                '5000_EXPENSES': {'name': 'المصروفات العامة (Expenses)', 'type': 'EXPENSE', 'arabic': 'المصروفات'},
                '1205_INV_EXCHANGE': {'name': 'المخزون - تبادل (Exchange Inventory)', 'type': 'ASSET', 'arabic': 'مخزون التبادل'},
                '2110_VAT_INPUT': {'name': 'ضريبة القيمة المضافة - مدخلات (VAT Input)', 'type': 'ASSET', 'arabic': 'مدخلات ضريبة'},
                '2155_ACCRUED_EXPENSES': {'name': 'مصاريف مستحقة (Accrued Expenses)', 'type': 'LIABILITY', 'arabic': 'مصاريف مستحقة'},
                '1130_PREPAID_EXPENSES': {'name': 'مصاريف مدفوعة مقدماً (Prepaid Expenses)', 'type': 'ASSET', 'arabic': 'مدفوعة مقدماً'},
                '2201_DUE_TO_PARTNER': {'name': 'مبالغ مستحقة للشريك (Due to Partner)', 'type': 'LIABILITY', 'arabic': 'مستحق للشريك'},
                '2202_DUE_FROM_PARTNER': {'name': 'مبالغ مستحقة من الشريك (Due from Partner)', 'type': 'ASSET', 'arabic': 'مستحق من الشريك'},
                '2300_ADVANCE_PAYMENTS': {'name': 'دفعات مقدمة (Advance Payments)', 'type': 'ASSET', 'arabic': 'دفعات مقدمة'},
                '2150_EMPLOYEE_ADVANCES': {'name': 'سلف الموظفين - تسوية (Employee Advances Clearing)', 'type': 'ASSET', 'arabic': 'سلف الموظفين'},
                '5105_COGS_EXCHANGE': {'name': 'تكلفة البضاعة المباعة - تبادل (COGS Exchange)', 'type': 'EXPENSE', 'arabic': 'تكلفة التبادل'},
                '1150_CHEQUES_RECEIVABLE': {'name': 'شيكات تحت التحصيل', 'type': 'ASSET', 'arabic': 'شيكات مدينة'},
                '2150_CHEQUES_PAYABLE': {'name': 'شيكات تحت الدفع', 'type': 'LIABILITY', 'arabic': 'شيكات دائنة'},
            },
            'accounting_principles': {
                'double_entry': {
                    'description': 'كل قيد محاسبي يجب أن يكون مزدوج (مدين ودائن متساويان)',
                    'example': 'بيع 1000 ₪ → مدين: 1100_AR (1000) | دائن: 4000_SALES (1000)',
                    'rule': 'مجموع المدين = مجموع الدائن'
                },
                'balance_calculation': {
                    'customer': 'الرصيد = (المبيعات + الفواتير + الخدمات) - (الدفعات الواردة) → سالب = عليه يدفع',
                    'supplier': 'الرصيد = (المشتريات + الشحنات) - (الدفعات الصادرة) → سالب = عليه يدفع',
                    'partner': 'الرصيد = (حصص المبيعات + الأرباح) - (التسويات) → موجب = له رصيد',
                    'memory_note': 'رصيد العميل: الشراء/الفاتورة/الخدمة → رصيد سالب (عليه يدفع) | الدفع IN → يزيد الرصيد | الدفع OUT → ينقص الرصيد'
                },
                'gl_entry_creation': {
                    'sale': 'عند البيع: مدين AR | دائن SALES (+ VAT إذا كان مفعل)',
                    'payment_in': 'دفع من عميل: مدين CASH/BANK/CARD | دائن AR',
                    'payment_out': 'دفع لمورد: مدين AP | دائن CASH/BANK',
                    'expense': 'مصروف: مدين EXPENSES | دائن CASH/BANK/AP',
                    'invoice_customer': 'فاتورة عميل: مدين AR | دائن SALES + VAT',
                    'invoice_supplier': 'فاتورة مورد: مدين PURCHASES | دائن AP',
                    'shipment_arrival': 'وصول شحنة: مدين INVENTORY | دائن AP',
                    'exchange_in': 'تبادل وارد: مدين INV_EXCHANGE | دائن AP',
                    'exchange_out': 'تبادل صادر: مدين COGS_EXCHANGE | دائن INV_EXCHANGE'
                },
                'vat_calculation': {
                    'palestine': {'rate': 16, 'description': 'ضريبة القيمة المضافة الفلسطينية'},
                    'israel': {'rate': 17, 'description': 'ضريبة القيمة المضافة الإسرائيلية'},
                    'formula': 'الضريبة = (المبلغ القابل للضريبة × معدل الضريبة) / 100',
                    'inclusive': 'إذا كان المبلغ شامل الضريبة: الصافي = الإجمالي / (1 + معدل الضريبة/100)'
                },
                'discount_rules': {
                    'service_parts': 'الخصم قيمة ثابتة (ليس نسبة) - يُطرح من الإجمالي قبل الضريبة',
                    'service_tasks': 'الخصم قيمة ثابتة (ليس نسبة) - يُطرح من الإجمالي قبل الضريبة',
                    'calculation': 'المبلغ بعد الخصم = (الكمية × السعر) - الخصم',
                    'tax_base': 'قاعدة الضريبة = المبلغ بعد الخصم (قبل إضافة الضريبة)'
                },
                'currency_exchange': {
                    'default': 'ILS (الشيقل الإسرائيلي)',
                    'fx_rate_used': 'كل عملية تحفظ سعر الصرف المستخدم في fx_rate_used',
                    'conversion': 'المبلغ بالشيقل = المبلغ الأصلي × سعر الصرف',
                    'memory': 'يتم حفظ fx_rate_used, fx_rate_source, fx_rate_timestamp تلقائياً'
                }
            },
            'financial_workflows': {
                'sale_complete': [
                    'إنشاء Sale مع SaleLines',
                    'تحديث StockLevel (نقص المخزون)',
                    'إنشاء GLBatch (مدين AR, دائن SALES)',
                    'تحديث رصيد العميل',
                    'تحديث رصيد الشركاء (إذا كان المنتج مرتبط بشركاء)'
                ],
                'payment_processing': [
                    'تسجيل Payment (IN/OUT)',
                    'ربط بالكيان (Customer/Supplier/Partner)',
                    'إنشاء GLBatch (مدين/دائن حسب الاتجاه)',
                    'تحديث رصيد الكيان',
                    'ربط بالعملية الأصلية (Sale/Invoice/Service)'
                ],
                'expense_recording': [
                    'تسجيل Expense',
                    'تصنيف (ExpenseType)',
                    'ربط بالكيان (Employee/Partner/Other)',
                    'إنشاء GLBatch (مدين EXPENSES, دائن CASH/BANK/AP)',
                    'تحديث رصيد الكيان (إذا كان مرتبط)'
                ],
                'service_request_complete': [
                    'تسجيل ServiceRequest',
                    'إضافة ServiceParts (قطع غيار)',
                    'إضافة ServiceTasks (عمالة)',
                    'حساب الإجمالي (أجزاء + عمالة - خصم)',
                    'إضافة الضريبة',
                    'تحديث المخزون (إذا consume_stock=True)',
                    'تحديث رصيد العميل'
                ]
            },
            'balance_formulas': {
                'customer_balance': {
                    'components': ['المبيعات', 'الفواتير', 'الخدمات', 'الدفعات الواردة (IN)', 'الدفعات الصادرة (OUT)'],
                    'formula': 'الرصيد = (المبيعات + الفواتير + الخدمات) - (الدفعات الواردة)',
                    'negative_meaning': 'رصيد سالب = العميل عليه (يجب أن يدفع)',
                    'positive_meaning': 'رصيد موجب = للعميل عندنا (دفع زيادة)'
                },
                'supplier_balance': {
                    'components': ['المشتريات', 'الشحنات', 'الدفعات الصادرة (OUT)', 'الدفعات الواردة (IN)'],
                    'formula': 'الرصيد = (المشتريات + الشحنات) - (الدفعات الصادرة)',
                    'negative_meaning': 'رصيد سالب = المورد عليه (يجب أن ندفع له)',
                    'positive_meaning': 'رصيد موجب = للمورد عندنا (دفعنا زيادة)'
                },
                'partner_balance': {
                    'components': ['حصص المبيعات', 'الأرباح', 'التسويات'],
                    'formula': 'الرصيد = (حصص المبيعات + الأرباح) - (التسويات)',
                    'positive_meaning': 'رصيد موجب = للشريك (له رصيد)',
                    'negative_meaning': 'رصيد سالب = على الشريك'
                }
            },
            'gl_account_types': {
                'ASSET': {'debit_increases': True, 'credit_increases': False, 'examples': ['AR', 'CASH', 'BANK', 'INVENTORY']},
                'LIABILITY': {'debit_increases': False, 'credit_increases': True, 'examples': ['AP', 'VAT_PAYABLE', 'CHEQUES_PAYABLE']},
                'REVENUE': {'debit_increases': False, 'credit_increases': True, 'examples': ['SALES', 'SERVICE_REVENUE']},
                'EXPENSE': {'debit_increases': True, 'credit_increases': False, 'examples': ['EXPENSES', 'COGS']},
                'EQUITY': {'debit_increases': False, 'credit_increases': True, 'examples': ['CAPITAL', 'RETAINED_EARNINGS']}
            }
        }
    
    def find_model_by_name(self, name):
        """البحث عن موديل بالاسم"""
        name_lower = name.lower()
        for model_name, model_data in self.knowledge['models'].items():
            if name_lower in model_name.lower():
                return {model_name: model_data}
        return None
    
    def find_related_models(self, model_name):
        """إيجاد الموديلات المرتبطة"""
        related = []
        for rel_key, rel_data in self.knowledge['relationships'].items():
            if rel_data['from'] == model_name:
                related.append(rel_data['to'])
            elif rel_data['to'] == model_name:
                related.append(rel_data['from'])
        return related
    
    def get_system_structure(self):
        """الحصول على هيكل النظام الكامل"""
        return {
            'models_count': len(self.knowledge['models']),
            'models': list(self.knowledge['models'].keys()),
            'routes_count': sum(len(r['routes']) for r in self.knowledge['routes'].values()),
            'templates_count': sum(len(t) for t in self.knowledge['templates'].values()),
            'relationships_count': len(self.knowledge['relationships']),
            'business_rules_count': len(self.knowledge['business_rules'])
        }
    
    def explain_model(self, model_name):
        """شرح موديل بالتفصيل"""
        if model_name not in self.knowledge['models']:
            return None
        
        model = self.knowledge['models'][model_name]
        related = self.find_related_models(model_name)
        
        explanation = f"""
📊 موديل: {model_name}
═════════════════════════════

📁 الملف: {model['file']}

📋 الأعمدة ({len(model['columns'])}):
{chr(10).join(f'  • {col}' for col in model['columns'][:10])}

🔗 العلاقات ({len(model['relationships'])}):
{chr(10).join(f'  → {rel}' for rel in model['relationships'])}

🤝 مرتبط بـ:
{chr(10).join(f'  ↔ {r}' for r in related)}
"""
        return explanation

class ErrorAnalyzer:
    """محلل الأخطاء - فهم وتفسير الأخطاء"""
    
    @staticmethod
    def analyze_traceback(traceback_text):
        """تحليل Traceback وتقديم حل"""
        analysis = {
            'error_type': 'Unknown',
            'file': 'Unknown',
            'line': 0,
            'cause': 'Unknown',
            'solution': 'Unknown',
            'severity': 'medium'
        }
        
        error_patterns = {
            'UndefinedError': {
                'cause': 'دالة أو متغير غير معرف في Template',
                'solution': 'تأكد من تسجيل الدالة كـ @app.template_global() أو تمريرها في render_template',
                'severity': 'high'
            },
            'NameError': {
                'cause': 'دالة أو متغير غير معرف في Python',
                'solution': 'تأكد من استيراد الدالة أو تعريفها قبل الاستخدام',
                'severity': 'high'
            },
            'AttributeError': {
                'cause': 'محاولة الوصول لخاصية غير موجودة',
                'solution': 'تأكد من وجود الخاصية أو استخدم getattr() مع قيمة افتراضية',
                'severity': 'medium'
            },
            'IntegrityError': {
                'cause': 'خرق قيد في قاعدة البيانات (Unique, Foreign Key)',
                'solution': 'تأكد من صحة البيانات قبل الحفظ، أو التعامل مع الخطأ',
                'severity': 'high'
            }
        }
        
        for error_name, error_info in error_patterns.items():
            if error_name in traceback_text:
                analysis['error_type'] = error_name
                analysis['cause'] = error_info['cause']
                analysis['solution'] = error_info['solution']
                analysis['severity'] = error_info['severity']
                break
        
        file_match = re.search(r'File "(.+?)", line (\d+)', traceback_text)
        if file_match:
            analysis['file'] = file_match.group(1)
            analysis['line'] = int(file_match.group(2))
        
        return analysis
    
    @staticmethod
    def format_error_response(analysis):
        """تنسيق رد الخطأ بشكل واضح"""
        severity_emoji = {
            'high': '🔴',
            'medium': '🟡',
            'low': '🟢'
        }
        
        return f"""
{severity_emoji.get(analysis['severity'], '⚠️')} **خطأ: {analysis['error_type']}**

📁 الملف: `{analysis['file']}`
📍 السطر: `{analysis['line']}`

💡 السبب:
{analysis['cause']}

🔧 الحل:
{analysis['solution']}
"""

_knowledge_base = None
_error_analyzer = ErrorAnalyzer()

def get_knowledge_base():
    """الحصول على قاعدة المعرفة (Singleton)"""
    global _knowledge_base
    if _knowledge_base is None:
        _knowledge_base = SystemKnowledgeBase()
        _knowledge_base.index_all_files()
    return _knowledge_base

def get_local_faq_responses():
    """قاعدة الأسئلة الشائعة - ردود فورية محلية"""
    return {
        'من أنت': """🤖 أنا المساعد الذكي في نظام أزاد لإدارة الكراجات (AI 4.0).
        
📌 قدراتي:
• قراءة مباشرة من قاعدة البيانات (87 جدول)
• حسابات مالية دقيقة (VAT، ضرائب، عملات)
• معرفة شاملة بـ 1,945 عنصر من النظام
• تدريب ذاتي مستمر
• وعي كامل بالنظام

🏢 النظام:
• الشركة: شركة أزاد للأنظمة الذكية
• المطور: المهندس أحمد غنام
• الموقع: رام الله - فلسطين 🇵🇸""",
        
        'ما قدراتك': """🧠 قدراتي الكاملة:

1. 📊 تحليل البيانات:
   • قراءة مباشرة من 87 جدول
   • إحصائيات فورية
   • تقارير مفصلة

2. 💰 الحسابات المالية:
   • VAT (16% فلسطين / 17% إسرائيل)
   • ضريبة الدخل
   • تحويل العملات
   • الأرباح والخسائر

3. 🧭 التنقل:
   • معرفة كل صفحات النظام (197 صفحة)
   • توجيه مباشر للوحدات
   
4. 🔧 الصيانة:
   • تحليل طلبات الصيانة
   • القطع المستخدمة
   • حالة الأعمال

5. 📦 المخزون:
   • مستويات المخزون
   • المستودعات (5 أنواع)
   • حركة القطع""",
        
        'كيف أضيف عميل': """📝 إضافة عميل جديد:

1. اذهب إلى: `/customers/add`
2. أدخل البيانات المطلوبة:
   • الاسم
   • رقم الهاتف
   • البريد الإلكتروني (اختياري)
   • العنوان
3. اضغط حفظ

🔗 الرابط المباشر: /customers/add""",
        
        'كيف أضيف صيانة': """🔧 إضافة طلب صيانة:

1. اذهب إلى: `/service/create`
2. اختر العميل
3. أدخل تفاصيل العطل
4. حدد الميكانيكي
5. أضف القطع المستخدمة (اختياري)
6. حفظ

🔗 الرابط: /service/create""",
        
        'أين النفقات': """💸 صفحة النفقات:

🔗 الرابط: `/expenses`

من هناك يمكنك:
• عرض جميع النفقات
• إضافة نفقة جديدة
• البحث والفلترة
• تصدير التقارير""",
        
        'أين المتجر': """🛒 المتجر الإلكتروني:

🔗 الرابط: `/shop`

الميزات:
• تصفح المنتجات
• سلة التسوق
• الطلبات المسبقة
• تقييم المنتجات""",
    }

def get_local_quick_rules():
    """قواعد الرد السريع المحلي - بدون Groq"""
    return {
        'count_customers': {
            'patterns': ['كم عدد العملاء', 'عدد الزبائن', 'how many customers'],
            'query': 'Customer.query.count()',
            'response_template': '✅ عدد العملاء: {count} عميل'
        },
        'count_services': {
            'patterns': ['كم صيانة', 'عدد الصيانات', 'طلبات الصيانة'],
            'query': 'ServiceRequest.query.count()',
            'response_template': '🔧 عدد طلبات الصيانة: {count} طلب'
        },
        'count_expenses': {
            'patterns': ['كم نفقة', 'عدد النفقات', 'المصاريف'],
            'query': 'Expense.query.count()',
            'response_template': '💸 عدد النفقات: {count} نفقة'
        },
        'count_products': {
            'patterns': ['كم منتج', 'عدد القطع', 'المنتجات'],
            'query': 'Product.query.count()',
            'response_template': '📦 عدد المنتجات: {count} منتج'
        },
        'count_suppliers': {
            'patterns': ['كم مورد', 'عدد الموردين'],
            'query': 'Supplier.query.count()',
            'response_template': '🏭 عدد الموردين: {count} مورد'
        },
    }

def analyze_error(traceback_text):
    """تحليل خطأ"""
    return _error_analyzer.analyze_traceback(traceback_text)

def format_error_response(analysis):
    """تنسيق رد الخطأ"""
    return _error_analyzer.format_error_response(analysis)

