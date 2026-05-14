"""Unified AI orchestration layer for AzadAccounting-sys.

This module is intentionally small and conservative. It does not replace the
existing AI engines yet; it wraps them behind one stable interface so routes and
future modules can talk to one AI entry point instead of importing many engines.

Design goals:
- single response contract
- safe fallback to the existing legacy ai_service
- light intent detection
- no direct data mutation
- no hard dependency on external LLM providers
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


@dataclass
class AIRequest:
    message: str
    user_id: Optional[int] = None
    username: Optional[str] = None
    session_id: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AIResult:
    success: bool
    response: str
    intent: str = "general"
    confidence: float = 0.0
    sources: List[Any] = field(default_factory=list)
    actions: List[Dict[str, Any]] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    mode: str = "unified"
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "response": self.response,
            "intent": self.intent,
            "confidence": self.confidence,
            "sources": self.sources,
            "actions": self.actions,
            "warnings": self.warnings,
            "mode": self.mode,
            "timestamp": self.timestamp,
        }


class UnifiedAI:
    """One safe entry point for AI requests."""

    WRITE_WORDS = (
        "أنشئ", "انشئ", "أضف", "اضف", "سجل", "احذف", "امسح", "عدّل", "عدل",
        "غيّر", "غير", "create", "add", "delete", "remove", "update", "modify",
    )

    def ask(self, request: AIRequest) -> AIResult:
        message = (request.message or "").strip()
        if not message:
            return AIResult(False, "الرسالة فارغة.", confidence=0.0, warnings=["empty_message"])

        intent = self.detect_intent(message)
        warnings = self.safety_warnings(message, intent)

        # For now, all executable/write intents are advisory only. This prevents
        # the AI layer from mutating accounting, inventory, users, or security data.
        actions: List[Dict[str, Any]] = []
        if warnings:
            actions.append({
                "type": "requires_confirmation",
                "message": "هذا الطلب قد يغيّر بيانات النظام، لذلك يبقى اقتراحًا فقط ولا يُنفّذ تلقائيًا.",
            })

        legacy = self.call_legacy_ai(message=message, session_id=request.session_id)
        if legacy.get("success") is False:
            return AIResult(
                success=False,
                response=legacy.get("response") or legacy.get("error") or "تعذر تشغيل المساعد الذكي.",
                intent=intent,
                confidence=0.0,
                sources=[],
                actions=actions,
                warnings=warnings + legacy.get("warnings", []),
                mode="unified:fallback_failed",
            )

        response_text = legacy.get("response") or "لم أتمكن من تكوين إجابة واضحة."
        confidence = self.normalize_confidence(legacy.get("confidence", 0.65))
        sources = legacy.get("sources", []) or []

        return AIResult(
            success=True,
            response=response_text,
            intent=intent,
            confidence=confidence,
            sources=sources,
            actions=actions,
            warnings=warnings,
            mode="unified:legacy_bridge",
        )

    def call_legacy_ai(self, message: str, session_id: Optional[str]) -> Dict[str, Any]:
        """Call the existing AI service lazily to avoid circular imports."""
        try:
            from AI.engine.ai_service import ai_chat_with_search

            result = ai_chat_with_search(message=message, session_id=session_id or "unified")
            if isinstance(result, dict):
                return {"success": True, **result}
            return {"success": True, "response": str(result), "confidence": 0.5, "sources": []}
        except Exception as exc:
            return {
                "success": False,
                "error": str(exc),
                "response": "حدث خطأ أثناء تشغيل محرك الذكاء الاصطناعي الحالي.",
                "warnings": ["legacy_ai_failed"],
            }

    def detect_intent(self, message: str) -> str:
        text = message.lower()
        if any(word in text for word in self.WRITE_WORDS):
            return "action_request"
        if any(word in text for word in ("عميل", "زبون", "customer", "customers")):
            return "customers"
        if any(word in text for word in ("قيد", "دفتر", "حساب", "ميزان", "محاس", "ledger", "accounting")):
            return "accounting"
        if any(word in text for word in ("مخزون", "مستودع", "قطعة", "منتج", "inventory", "warehouse", "product")):
            return "inventory"
        if any(word in text for word in ("تقرير", "تحليل", "إحص", "report", "analysis")):
            return "reporting"
        if any(word in text for word in ("خطأ", "مشكلة", "تعطل", "error", "bug", "traceback")):
            return "troubleshooting"
        if any(word in text for word in ("افتح", "اذهب", "صفحة", "رابط", "navigation")):
            return "navigation"
        return "general"

    def safety_warnings(self, message: str, intent: str) -> List[str]:
        warnings: List[str] = []
        if intent == "action_request":
            warnings.append("write_intent_detected")
        risky_words = ("احذف", "امسح", "delete", "drop", "truncate", "hard delete", "restore database")
        if any(word in message.lower() for word in risky_words):
            warnings.append("dangerous_operation_requested")
        return warnings

    def normalize_confidence(self, value: Any) -> float:
        try:
            num = float(value)
        except Exception:
            return 0.0
        if num > 1:
            num = num / 100.0
        if num < 0:
            return 0.0
        if num > 1:
            return 1.0
        return round(num, 3)


def ask_unified_ai(
    message: str,
    *,
    user: Any = None,
    session_id: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    request = AIRequest(
        message=message,
        user_id=getattr(user, "id", None),
        username=getattr(user, "username", None),
        session_id=session_id,
        context=context or {},
    )
    return UnifiedAI().ask(request).to_dict()
