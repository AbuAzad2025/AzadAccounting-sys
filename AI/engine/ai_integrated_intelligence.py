"""
AI Integrated Intelligence - الذكاء المتكامل الحقيقي
"""

from typing import Dict, List, Any, Optional, Tuple
import json
import os
import re
from datetime import datetime
from decimal import Decimal


class IntegratedIntelligence:
    
    def __init__(self):
        self.experts = {}
        self.knowledge_db = {}
        self.interaction_history = []
        self.learning_system = None
        self._initialize_experts()
        self._load_knowledge()
        self._initialize_learning()
    
    def _initialize_experts(self):
        try:
            from AI.engine.ai_python_expert import get_python_expert
            from AI.engine.ai_database_expert import get_database_expert  
            from AI.engine.ai_web_expert import get_web_expert
            from AI.engine.ai_user_guide_master import get_user_guide_master
            
            self.experts['python'] = get_python_expert()
            self.experts['database'] = get_database_expert()
            self.experts['web'] = get_web_expert()
            self.experts['guide'] = get_user_guide_master()
        except Exception as e:
            print(f"Error loading experts: {e}")
    
    def _load_knowledge(self):
        knowledge_files = [
            'AI/data/complete_system_knowledge.json',
            'AI/data/professional_accountant_training.json',
            'AI/data/massive_knowledge_base.json'
        ]
        
        for kf in knowledge_files:
            if os.path.exists(kf):
                try:
                    with open(kf, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        self.knowledge_db.update(data)
                except Exception:
                    pass
    
    def _initialize_learning(self):
        try:
            from AI.engine.ai_learning_system import get_learning_system
            self.learning_system = get_learning_system()
        except Exception:
            pass
    
    def process_query(self, query: str, context: Dict) -> Dict[str, Any]:
        if self.learning_system:
            learned_response = self.learning_system.get_learned_response(query)
            if learned_response:
                return {
                    'answer': learned_response,
                    'confidence': 0.95,
                    'sources': ['Memory'],
                    'tips': []
                }
        
        q_lower = query.lower()
        response_parts = []
        confidence = 0.5
        sources = []
        
        is_action_request = any(w in q_lower for w in ['أضف', 'add', 'create', 'سجل', 'register', 'حذف', 'احذف', 'delete', 'remove', 'أزل', 'أرشف', 'أرشفة', 'ارشفة', 'ارشف', 'archive', 'عكس', 'reverse', 'تصحيح', 'اصلاح', 'fix'])
        
        if is_action_request:
            action_result = self._handle_action_request(query, context)
            if action_result:
                return action_result
        
        if any(w in q_lower for w in ['error', 'خطأ', 'مشكلة', 'bug']):
            if self.experts.get('python'):
                try:
                    result = self.experts['python'].analyze_error(query, context.get('code', ''))
                    if result:
                        response_parts.append(f"نوع الخطأ: {result.get('error_type', 'غير محدد')}")
                        response_parts.append(f"السبب: {result.get('cause', '')}")
                        
                        if result.get('solutions'):
                            response_parts.append('\nالحلول:')
                            response_parts.extend([f"{i+1}. {sol}" for i, sol in enumerate(result['solutions'][:3])])
                        
                        if result.get('code_fix'):
                            response_parts.append(f"\nالكود الصحيح:\n{result['code_fix']}")
                        
                        confidence = 0.9
                        sources.append('Python Expert')
                except Exception as e:
                    print(f"Python Expert error: {e}")
        
        if any(w in q_lower for w in ['كيف', 'how', 'خطوات', 'steps', 'طريقة', 'ماذا', 'what']):
            if self.experts.get('guide'):
                try:
                    result = self.experts['guide'].answer_question(query)
                    if result and isinstance(result, dict):
                        parts = []
                        
                        if result.get('topic'):
                            parts.append(f"📍 {result['topic']}")
                        
                        if result.get('description'):
                            parts.append(result['description'])
                        
                        if result.get('route'):
                            parts.append(f"\n🔗 المسار: {result['route']}")
                        
                        if result.get('steps') and isinstance(result['steps'], list):
                            parts.append('\n📋 الخطوات:')
                            parts.extend(result['steps'])
                        
                        if result.get('fields') and isinstance(result['fields'], dict):
                            parts.append('\n📝 الحقول المطلوبة:')
                            for field, desc in result['fields'].items():
                                parts.append(f"  • {field}: {desc}")
                        
                        if result.get('tips') and isinstance(result['tips'], list):
                            parts.append('\n💡 نصائح مهمة:')
                            for tip in result['tips']:
                                parts.append(f"  - {tip}")
                        
                        if result.get('gl_effect'):
                            parts.append(f"\n💼 التأثير المحاسبي:\n{result['gl_effect']}")
                        
                        if parts:
                            response_parts.extend(parts)
                            confidence = max(confidence, 0.9)
                            sources.append('User Guide')
                except Exception as e:
                    print(f"Guide error: {e}")
        
        if any(w in q_lower for w in ['رصيد', 'balance', 'حساب', 'مبلغ', 'كم']):
            try:
                search_results = context.get('search_results', {})
                
                if search_results.get('customers'):
                    response_parts.append('📊 أرصدة العملاء:')
                    
                    for cust in search_results['customers'][:5]:
                        name = cust.get('name', '')
                        balance = float(cust.get('balance', 0))
                        
                        if balance > 0:
                            response_parts.append(f"  • {name}: عليه {balance:.2f} ₪ (مدين)")
                        elif balance < 0:
                            response_parts.append(f"  • {name}: له {abs(balance):.2f} ₪ (دائن)")
                        else:
                            response_parts.append(f"  • {name}: رصيد متعادل (0.00 ₪)")
                    
                    total_balance = sum(float(c.get('balance', 0)) for c in search_results['customers'])
                    response_parts.append(f"\n💰 الإجمالي: {total_balance:.2f} ₪")
                    
                    response_parts.append('\n💼 من الناحية المحاسبية:')
                    response_parts.append('  - الرصيد الموجب = العميل عليه (ذمم مدينة)')
                    response_parts.append('  - الرصيد السالب = العميل له (ذمم دائنة)')
                    response_parts.append('  - الحساب المحاسبي: 1300 - ذمم العملاء')
                    
                    confidence = max(confidence, 0.9)
                    sources.append('Database + Accounting')
                
                elif search_results.get('suppliers'):
                    response_parts.append('📊 أرصدة الموردين:')
                    
                    for sup in search_results['suppliers'][:5]:
                        name = sup.get('name', '')
                        balance = float(sup.get('balance', 0))
                        
                        if balance < 0:
                            response_parts.append(f"  • {name}: ندين له {abs(balance):.2f} ₪")
                        elif balance > 0:
                            response_parts.append(f"  • {name}: دائن لنا {balance:.2f} ₪")
                        else:
                            response_parts.append(f"  • {name}: متعادل (0.00 ₪)")
                    
                    response_parts.append('\n💼 الحساب المحاسبي: 2300 - ذمم الموردين')
                    confidence = max(confidence, 0.9)
                    sources.append('Database + Accounting')
                
                else:
                    response_parts.append('لم أجد بيانات عن العميل/المورد المطلوب.')
                    response_parts.append('\nيمكنك:')
                    response_parts.append('1. البحث في صفحة العملاء: /customers')
                    response_parts.append('2. عرض كشف حساب محدد')
                    confidence = 0.6
            
            except Exception as e:
                print(f"Balance query error: {e}")
        
        if any(w in q_lower for w in ['بيع', 'مبيعات', 'sale', 'فاتورة']):
            try:
                search_results = context.get('search_results', {})
                
                if search_results.get('sales'):
                    response_parts.append('المبيعات:')
                    total_sales = sum(float(s.get('total', 0)) for s in search_results['sales'][:10])
                    response_parts.append(f"عدد الفواتير: {len(search_results['sales'])}")
                    response_parts.append(f"الإجمالي: {total_sales:.2f} ₪")
                    confidence = max(confidence, 0.8)
                    sources.append('Sales Data')
            except Exception as e:
                print(f"Sales query error: {e}")
        
        if not response_parts:
            try:
                from AI.engine.ai_database_search import search_in_database
                db_data = search_in_database(query)
                if db_data:
                    response_parts.append(str(db_data))
                    confidence = 0.7
                    sources.append('Database Search')
            except Exception:
                pass
        
        final_answer = '\n'.join(response_parts) if response_parts else self._fallback_response(query)
        
        if not response_parts:
            confidence = 0.6
        
        self.interaction_history.append({
            'query': query,
            'timestamp': datetime.now().isoformat(),
            'confidence': confidence,
            'sources': sources
        })
        
        self._save_interaction_history()
        
        if self.learning_system and final_answer:
            self.learning_system.learn_from_interaction(query, final_answer)
        
        return {
            'answer': final_answer,
            'confidence': confidence,
            'sources': sources,
            'tips': []
        }
    
    def _save_interaction_history(self):
        try:
            os.makedirs('AI/data', exist_ok=True)
            history_file = 'AI/data/interaction_history.json'
            
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(self.interaction_history[-500:], f, ensure_ascii=False, indent=2)
        except Exception:
            pass
    
    def _handle_action_request(self, query: str, context: Dict) -> Optional[Dict]:
        try:
            from AI.engine.ai_action_executor import ActionExecutor
            from AI.engine.ai_permissions import can_ai_execute_action
            from models import SystemSettings
            
            user_id = context.get('user_id')
            if not user_id:
                return None
            
            if not bool(SystemSettings.get_setting('ai_can_execute_actions', True)):
                return {
                    'answer': 'تنفيذ العمليات عبر المساعد معطّل حالياً',
                    'confidence': 0.4,
                    'sources': ['AI Settings'],
                    'tips': [],
                    'action_executed': False,
                    'action_result': {'success': False, 'message': 'تنفيذ العمليات معطّل'}
                }
            
            action_type, params = self._parse_action_from_query(query, context)
            if not action_type or not params:
                return None
            
            if not can_ai_execute_action(action_type, context.get('user_role', '') or ''):
                return {
                    'answer': 'ليس لديك صلاحية لتنفيذ هذا الإجراء',
                    'confidence': 0.5,
                    'sources': ['Permissions'],
                    'tips': [],
                    'action_executed': False,
                    'action_result': {'success': False, 'message': 'صلاحيات غير كافية'}
                }
            
            executor = ActionExecutor(user_id)
            result = executor.execute_action(action_type, params)
            
            return {
                'answer': result.get('message', 'تم التنفيذ'),
                'confidence': 0.9 if result.get('success') else 0.5,
                'sources': ['Action Executor'],
                'tips': [],
                'action_executed': True,
                'action_result': result
            }
        
        except Exception as e:
            print(f"Action execution error: {e}")
        
        return None
    
    def _parse_action_from_query(self, query: str, context: Dict) -> Tuple[Optional[str], Optional[Dict]]:
        q_lower = query.lower()
        
        if 'أضف عميل' in q_lower or 'add customer' in q_lower:
            return ('add_customer', {
                'name': self._extract_name(query),
                'phone': self._extract_phone(query)
            })
        
        if 'أضف منتج' in q_lower or 'add product' in q_lower:
            return ('add_product', {
                'name': self._extract_name(query),
                'cost_price': self._extract_price(query, 'cost'),
                'selling_price': self._extract_price(query, 'sell')
            })

        split_refs = re.findall(r"SPLIT-\d+-PMT-\d+", query, re.IGNORECASE)
        if split_refs and any(w in q_lower for w in ['حذف', 'احذف', 'delete', 'remove', 'أزل']):
            raw_refs = " ".join([r.upper() for r in split_refs])
            return ('delete_split_ref', {'raw_refs': raw_refs})
        
        split_match = re.search(r"(?:split|سبليت)\s*(?:رقم)?\s*#?\s*(\d+)", q_lower)
        if split_match and any(w in q_lower for w in ['حذف', 'احذف', 'delete', 'remove', 'أزل']):
            return ('delete_split', {'split_id': int(split_match.group(1))})
        
        payment_match = re.search(r"(?:دفعة|payment|pmt)\s*(?:رقم)?\s*#?\s*(\d+)", q_lower)
        if payment_match and any(w in q_lower for w in ['حذف', 'احذف', 'delete', 'remove', 'أزل']):
            return ('delete_payment', {'payment_id': int(payment_match.group(1))})
        
        check_match = re.search(r"(?:شيك|check)\s*(?:رقم)?\s*#?\s*(\d+)", q_lower)
        if check_match and any(w in q_lower for w in ['حذف', 'احذف', 'delete', 'remove', 'أزل']):
            return ('delete_check', {'check_id': int(check_match.group(1))})
        
        expense_match = re.search(r"(?:مصروف|expense)\s*(?:رقم)?\s*#?\s*(\d+)", q_lower)
        if expense_match and any(w in q_lower for w in ['حذف', 'احذف', 'delete', 'remove', 'أزل']):
            return ('delete_expense', {'expense_id': int(expense_match.group(1))})

        delete_words = ['حذف', 'احذف', 'delete', 'remove', 'أزل']
        archive_words = ['أرشف', 'أرشفة', 'ارشفة', 'ارشف', 'archive']
        sale_match = re.search(r"(?:مبيعة|مبيعات|بيع|sale|invoice)\s*(?:رقم)?\s*#?\s*(\d+)", q_lower)
        if sale_match and any(w in q_lower for w in delete_words):
            return ('delete_sale', {'sale_id': int(sale_match.group(1))})
        if sale_match and any(w in q_lower for w in archive_words):
            return ('archive_sale', {'sale_id': int(sale_match.group(1))})

        if check_match and any(w in q_lower for w in archive_words):
            return ('archive_check', {'check_id': int(check_match.group(1))})

        if expense_match and any(w in q_lower for w in archive_words):
            return ('archive_expense', {'expense_id': int(expense_match.group(1))})

        entry_match = re.search(r"(?:قيد|batch|entry)\s*(?:رقم)?\s*#?\s*(\d+)", q_lower)
        if entry_match and any(w in q_lower for w in delete_words + archive_words):
            return ('void_gl_batch', {'batch_id': int(entry_match.group(1))})
        if entry_match and any(w in q_lower for w in ['عكس', 'reverse', 'reversal']):
            return ('reverse_gl_batch', {'batch_id': int(entry_match.group(1))})

        if any(w in q_lower for w in ['غير متوازنة', 'unbalanced', 'تصحيح القيود', 'إصلاح القيود', 'fix unbalanced']):
            return ('fix_unbalanced_batches', {'scope': 'all'})
        
        return (None, None)
    
    def _extract_name(self, query: str) -> str:
        match = re.search(r'اسمه?:?\s+([^\s،.]+)', query)
        if match:
            return match.group(1)
        
        match = re.search(r'name:?\s+(\w+)', query, re.IGNORECASE)
        if match:
            return match.group(1)
        
        return ''
    
    def _extract_phone(self, query: str) -> str:
        match = re.search(r'(\d{10}|\d{9})', query)
        if match:
            return match.group(1)
        return ''
    
    def _extract_price(self, query: str, price_type: str) -> float:
        if price_type == 'cost':
            match = re.search(r'تكلفة:?\s+(\d+(?:\.\d+)?)', query)
        else:
            match = re.search(r'سعر:?\s+(\d+(?:\.\d+)?)', query)
        
        if match:
            return float(match.group(1))
        return 0.0
    
    def _fallback_response(self, query: str) -> str:
        q_lower = query.lower()
        
        if 'عميل' in q_lower or 'customer' in q_lower:
            return "العملاء: /customers\nإضافة عميل: /customers/create"
        
        if 'بيع' in q_lower or 'sale' in q_lower:
            return "المبيعات: /sales\nإنشاء فاتورة: /sales/create"
        
        if 'منتج' in q_lower or 'product' in q_lower:
            return "المنتجات: /products\nإضافة منتج: /products/create"
        
        return "يمكنني مساعدتك في: العملاء، المبيعات، المنتجات، المحاسبة، الصيانة"


_integrated_intelligence = None

def get_integrated_intelligence():
    global _integrated_intelligence
    if _integrated_intelligence is None:
        _integrated_intelligence = IntegratedIntelligence()
    return _integrated_intelligence


__all__ = ['IntegratedIntelligence', 'get_integrated_intelligence']

