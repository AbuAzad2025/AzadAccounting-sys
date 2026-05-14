"""AI Integrated Intelligence.

Coordinates domain experts, learned responses, database context, and safe action
requests. Runtime JSON reads/writes go through ai_storage.
"""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any, Dict, Optional, Tuple

from AI.engine.ai_storage import read_json, sync_training_manifest, write_json

INTERACTION_HISTORY_FILE = "interaction_history.json"
KNOWLEDGE_FILES = (
    "complete_system_knowledge.json",
    "professional_accountant_training.json",
    "massive_knowledge_base.json",
)


class IntegratedIntelligence:
    def __init__(self):
        self.experts = {}
        self.knowledge_db = {}
        self.interaction_history = []
        self.learning_system = None
        self._initialize_experts()
        self._load_knowledge()
        self._initialize_learning()
        self._load_interaction_history()

    def _initialize_experts(self):
        expert_factories = {
            "python": ("AI.engine.ai_python_expert", "get_python_expert"),
            "database": ("AI.engine.ai_database_expert", "get_database_expert"),
            "web": ("AI.engine.ai_web_expert", "get_web_expert"),
            "guide": ("AI.engine.ai_user_guide_master", "get_user_guide_master"),
        }
        for name, (module_path, factory_name) in expert_factories.items():
            try:
                module = __import__(module_path, fromlist=[factory_name])
                self.experts[name] = getattr(module, factory_name)()
            except Exception as exc:
                self.experts[name] = None
                print(f"Error loading expert [{name}]: {exc}")

    def _load_knowledge(self):
        for filename in KNOWLEDGE_FILES:
            data = read_json(filename, None)
            if isinstance(data, dict):
                self.knowledge_db.update(data)

    def _initialize_learning(self):
        try:
            from AI.engine.ai_learning_system import get_learning_system

            self.learning_system = get_learning_system()
        except Exception:
            self.learning_system = None

    def _load_interaction_history(self):
        data = read_json(INTERACTION_HISTORY_FILE, [])
        self.interaction_history = data[-500:] if isinstance(data, list) else []

    def process_query(self, query: str, context: Dict) -> Dict[str, Any]:
        context = context or {}
        if self.learning_system:
            learned_response = self.learning_system.get_learned_response(query)
            if learned_response:
                return {"answer": learned_response, "confidence": 0.95, "sources": ["Memory"], "tips": []}

        q_lower = str(query or "").lower()
        response_parts = []
        confidence = 0.5
        sources = []

        is_action_request = any(
            w in q_lower
            for w in [
                "أضف",
                "اضف",
                "add",
                "create",
                "سجل",
                "register",
                "حذف",
                "احذف",
                "delete",
                "remove",
                "أزل",
                "ازل",
                "أرشف",
                "ارشفة",
                "archive",
                "عكس",
                "reverse",
                "تصحيح",
                "اصلاح",
                "fix",
            ]
        )
        if is_action_request:
            action_result = self._handle_action_request(query, context)
            if action_result:
                return action_result

        if any(w in q_lower for w in ["error", "خطأ", "مشكلة", "bug"]):
            self._use_python_expert(query, context, response_parts, sources)
            if response_parts:
                confidence = max(confidence, 0.9)

        if any(w in q_lower for w in ["كيف", "how", "خطوات", "steps", "طريقة", "ماذا", "what"]):
            if self._use_guide_expert(query, response_parts, sources):
                confidence = max(confidence, 0.9)

        if any(w in q_lower for w in ["رصيد", "balance", "حساب", "مبلغ", "كم"]):
            handled, new_confidence = self._handle_balance_query(context, response_parts, sources)
            if handled:
                confidence = max(confidence, new_confidence)

        if any(w in q_lower for w in ["بيع", "مبيعات", "sale", "فاتورة"]):
            handled, new_confidence = self._handle_sales_query(context, response_parts, sources)
            if handled:
                confidence = max(confidence, new_confidence)

        if not response_parts:
            try:
                from AI.engine.ai_database_search import search_in_database

                db_data = search_in_database(query)
                if db_data:
                    response_parts.append(str(db_data))
                    confidence = 0.7
                    sources.append("Database Search")
            except Exception:
                pass

        final_answer = "\n".join(response_parts) if response_parts else self._fallback_response(query)
        if not response_parts:
            confidence = 0.6

        self.interaction_history.append(
            {"query": str(query or "")[:200], "timestamp": datetime.now().isoformat(), "confidence": confidence, "sources": sources}
        )
        self.interaction_history = self.interaction_history[-500:]
        self._save_interaction_history()

        if self.learning_system and final_answer:
            self.learning_system.learn_from_interaction(query, final_answer)

        return {"answer": final_answer, "confidence": confidence, "sources": sources, "tips": []}

    def _use_python_expert(self, query: str, context: Dict, response_parts: list, sources: list) -> None:
        expert = self.experts.get("python")
        if not expert:
            return
        try:
            result = expert.analyze_error(query, context.get("code", ""))
            if not result:
                return
            response_parts.append(f"نوع الخطأ: {result.get('error_type', 'غير محدد')}")
            response_parts.append(f"السبب: {result.get('cause', '')}")
            if result.get("solutions"):
                response_parts.append("\nالحلول:")
                response_parts.extend([f"{i + 1}. {sol}" for i, sol in enumerate(result["solutions"][:3])])
            if result.get("code_fix"):
                response_parts.append(f"\nالكود الصحيح:\n{result['code_fix']}")
            sources.append("Python Expert")
        except Exception as exc:
            print(f"Python Expert error: {exc}")

    def _use_guide_expert(self, query: str, response_parts: list, sources: list) -> bool:
        expert = self.experts.get("guide")
        if not expert:
            return False
        try:
            result = expert.answer_question(query)
            if not result or not isinstance(result, dict):
                return False
            parts = []
            if result.get("topic"):
                parts.append(f"📍 {result['topic']}")
            if result.get("description"):
                parts.append(result["description"])
            if result.get("route"):
                parts.append(f"\n🔗 المسار: {result['route']}")
            if isinstance(result.get("steps"), list):
                parts.append("\n📋 الخطوات:")
                parts.extend(result["steps"])
            if isinstance(result.get("fields"), dict):
                parts.append("\n📝 الحقول المطلوبة:")
                for field, desc in result["fields"].items():
                    parts.append(f"  • {field}: {desc}")
            if isinstance(result.get("tips"), list):
                parts.append("\n💡 نصائح مهمة:")
                for tip in result["tips"]:
                    parts.append(f"  - {tip}")
            if result.get("gl_effect"):
                parts.append(f"\n💼 التأثير المحاسبي:\n{result['gl_effect']}")
            if parts:
                response_parts.extend(parts)
                sources.append("User Guide")
                return True
        except Exception as exc:
            print(f"Guide error: {exc}")
        return False

    def _handle_balance_query(self, context: Dict, response_parts: list, sources: list) -> Tuple[bool, float]:
        try:
            search_results = context.get("search_results", {})
            if search_results.get("customers"):
                response_parts.append("📊 أرصدة العملاء:")
                for cust in search_results["customers"][:5]:
                    name = cust.get("name", "")
                    balance = float(cust.get("balance", 0) or 0)
                    if balance > 0:
                        response_parts.append(f"  • {name}: عليه {balance:.2f} ₪ (مدين)")
                    elif balance < 0:
                        response_parts.append(f"  • {name}: له {abs(balance):.2f} ₪ (دائن)")
                    else:
                        response_parts.append(f"  • {name}: رصيد متعادل (0.00 ₪)")
                total_balance = sum(float(c.get("balance", 0) or 0) for c in search_results["customers"])
                response_parts.append(f"\n💰 الإجمالي: {total_balance:.2f} ₪")
                response_parts.append("\n💼 من الناحية المحاسبية:")
                response_parts.append("  - الرصيد الموجب = العميل عليه (ذمم مدينة)")
                response_parts.append("  - الرصيد السالب = العميل له (ذمم دائنة)")
                response_parts.append("  - الحساب المحاسبي: 1300 - ذمم العملاء")
                sources.append("Database + Accounting")
                return True, 0.9
            if search_results.get("suppliers"):
                response_parts.append("📊 أرصدة الموردين:")
                for sup in search_results["suppliers"][:5]:
                    name = sup.get("name", "")
                    balance = float(sup.get("balance", 0) or 0)
                    if balance < 0:
                        response_parts.append(f"  • {name}: ندين له {abs(balance):.2f} ₪")
                    elif balance > 0:
                        response_parts.append(f"  • {name}: دائن لنا {balance:.2f} ₪")
                    else:
                        response_parts.append(f"  • {name}: متعادل (0.00 ₪)")
                response_parts.append("\n💼 الحساب المحاسبي: 2300 - ذمم الموردين")
                sources.append("Database + Accounting")
                return True, 0.9
        except Exception as exc:
            print(f"Balance query error: {exc}")
        return False, 0.0

    def _handle_sales_query(self, context: Dict, response_parts: list, sources: list) -> Tuple[bool, float]:
        try:
            search_results = context.get("search_results", {})
            if search_results.get("sales"):
                response_parts.append("المبيعات:")
                total_sales = sum(float(s.get("total", 0) or 0) for s in search_results["sales"][:10])
                response_parts.append(f"عدد الفواتير: {len(search_results['sales'])}")
                response_parts.append(f"الإجمالي: {total_sales:.2f} ₪")
                sources.append("Sales Data")
                return True, 0.8
        except Exception as exc:
            print(f"Sales query error: {exc}")
        return False, 0.0

    def _save_interaction_history(self):
        try:
            write_json(INTERACTION_HISTORY_FILE, self.interaction_history[-500:])
            sync_training_manifest(extra_files=[INTERACTION_HISTORY_FILE])
        except Exception:
            pass

    def _handle_action_request(self, query: str, context: Dict) -> Optional[Dict]:
        try:
            from AI.engine.ai_action_executor import ActionExecutor
            from AI.engine.ai_permissions import can_ai_execute_action
            from models import SystemSettings

            user_id = context.get("user_id")
            if not user_id:
                return None
            if not bool(SystemSettings.get_setting("ai_can_execute_actions", True)):
                return {
                    "answer": "تنفيذ العمليات عبر المساعد معطّل حالياً",
                    "confidence": 0.4,
                    "sources": ["AI Settings"],
                    "tips": [],
                    "action_executed": False,
                    "action_result": {"success": False, "message": "تنفيذ العمليات معطّل"},
                }
            action_type, params = self._parse_action_from_query(query, context)
            if not action_type or not params:
                return None
            if not can_ai_execute_action(action_type, context.get("user_role", "") or ""):
                return {
                    "answer": "لا أستطيع تنفيذ هذا الإجراء تلقائيًا. قد يكون خطيرًا أو يحتاج صلاحية/تأكيد يدوي.",
                    "confidence": 0.5,
                    "sources": ["Permissions"],
                    "tips": [],
                    "action_executed": False,
                    "action_result": {"success": False, "message": "غير مسموح للـ AI بتنفيذ هذا الإجراء"},
                }
            executor = ActionExecutor(user_id)
            result = executor.execute_action(action_type, params)
            return {
                "answer": result.get("message", "تم التنفيذ"),
                "confidence": 0.9 if result.get("success") else 0.5,
                "sources": ["Action Executor"],
                "tips": [],
                "action_executed": True,
                "action_result": result,
            }
        except Exception as exc:
            print(f"Action execution error: {exc}")
        return None

    def _parse_action_from_query(self, query: str, context: Dict) -> Tuple[Optional[str], Optional[Dict]]:
        q_lower = str(query or "").lower()
        if "أضف عميل" in q_lower or "اضف عميل" in q_lower or "add customer" in q_lower:
            return "add_customer", {"name": self._extract_name(query), "phone": self._extract_phone(query)}
        if "أضف منتج" in q_lower or "اضف منتج" in q_lower or "add product" in q_lower:
            return "add_product", {"name": self._extract_name(query), "cost_price": self._extract_price(query, "cost"), "selling_price": self._extract_price(query, "sell")}

        split_refs = re.findall(r"SPLIT-\d+-PMT-\d+", query, re.IGNORECASE)
        if split_refs and self._contains_delete(q_lower):
            return "delete_split_ref", {"raw_refs": " ".join([r.upper() for r in split_refs])}

        patterns = [
            (r"(?:split|سبليت)\s*(?:رقم)?\s*#?\s*(\d+)", "delete_split", "split_id"),
            (r"(?:دفعة|payment|pmt)\s*(?:رقم)?\s*#?\s*(\d+)", "delete_payment", "payment_id"),
            (r"(?:شيك|check)\s*(?:رقم)?\s*#?\s*(\d+)", "delete_check", "check_id"),
            (r"(?:مصروف|expense)\s*(?:رقم)?\s*#?\s*(\d+)", "delete_expense", "expense_id"),
            (r"(?:مبيعة|مبيعات|بيع|sale|invoice)\s*(?:رقم)?\s*#?\s*(\d+)", "delete_sale", "sale_id"),
        ]
        for pattern, action, key in patterns:
            match = re.search(pattern, q_lower)
            if match and self._contains_delete(q_lower):
                return action, {key: int(match.group(1))}

        sale_match = re.search(r"(?:مبيعة|مبيعات|بيع|sale|invoice)\s*(?:رقم)?\s*#?\s*(\d+)", q_lower)
        if sale_match and self._contains_archive(q_lower):
            return "archive_sale", {"sale_id": int(sale_match.group(1))}

        check_match = re.search(r"(?:شيك|check)\s*(?:رقم)?\s*#?\s*(\d+)", q_lower)
        if check_match and self._contains_archive(q_lower):
            return "archive_check", {"check_id": int(check_match.group(1))}

        expense_match = re.search(r"(?:مصروف|expense)\s*(?:رقم)?\s*#?\s*(\d+)", q_lower)
        if expense_match and self._contains_archive(q_lower):
            return "archive_expense", {"expense_id": int(expense_match.group(1))}

        entry_match = re.search(r"(?:قيد|batch|entry)\s*(?:رقم)?\s*#?\s*(\d+)", q_lower)
        if entry_match and (self._contains_delete(q_lower) or self._contains_archive(q_lower)):
            return "void_gl_batch", {"batch_id": int(entry_match.group(1))}
        if entry_match and any(w in q_lower for w in ["عكس", "reverse", "reversal"]):
            return "reverse_gl_batch", {"batch_id": int(entry_match.group(1))}
        if any(w in q_lower for w in ["غير متوازنة", "unbalanced", "تصحيح القيود", "إصلاح القيود", "fix unbalanced"]):
            return "fix_unbalanced_batches", {"scope": "all"}
        return None, None

    def _contains_delete(self, text: str) -> bool:
        return any(w in text for w in ["حذف", "احذف", "delete", "remove", "أزل", "ازل"])

    def _contains_archive(self, text: str) -> bool:
        return any(w in text for w in ["أرشف", "أرشفة", "ارشفة", "ارشف", "archive"])

    def _extract_name(self, query: str) -> str:
        match = re.search(r"اسمه?:?\s+([^\s،.]+)", query)
        if match:
            return match.group(1)
        match = re.search(r"name:?\s+(\w+)", query, re.IGNORECASE)
        return match.group(1) if match else ""

    def _extract_phone(self, query: str) -> str:
        match = re.search(r"(\d{10}|\d{9})", query)
        return match.group(1) if match else ""

    def _extract_price(self, query: str, price_type: str) -> float:
        match = re.search(r"تكلفة:?\s+(\d+(?:\.\d+)?)", query) if price_type == "cost" else re.search(r"سعر:?\s+(\d+(?:\.\d+)?)", query)
        return float(match.group(1)) if match else 0.0

    def _fallback_response(self, query: str) -> str:
        q_lower = str(query or "").lower()
        if "عميل" in q_lower or "customer" in q_lower:
            return "العملاء: /customers\nإضافة عميل: /customers/create"
        if "بيع" in q_lower or "sale" in q_lower:
            return "المبيعات: /sales\nإنشاء فاتورة: /sales/create"
        if "منتج" in q_lower or "product" in q_lower:
            return "المنتجات: /products\nإضافة منتج: /products/create"
        return "يمكنني مساعدتك في: العملاء، المبيعات، المنتجات، المحاسبة، الصيانة"


_integrated_intelligence = None


def get_integrated_intelligence():
    global _integrated_intelligence
    if _integrated_intelligence is None:
        _integrated_intelligence = IntegratedIntelligence()
    return _integrated_intelligence


__all__ = ["IntegratedIntelligence", "get_integrated_intelligence"]
