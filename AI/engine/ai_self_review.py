"""AI self-review utilities.

Keeps a compact interaction log, analyzes recent response quality, and writes a
self-audit report. Runtime JSON files are handled through ai_storage so the AI
layer uses one storage policy.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict

from AI.engine.ai_storage import append_json_list, read_json, sync_training_manifest, utc_now, write_json

INTERACTIONS_LOG = "ai_interactions.json"
SELF_AUDIT_LOG = "ai_self_audit.json"
TRAINING_POLICY = "ai_training_policy.json"


def log_interaction(question, answer, confidence, search_results):
    try:
        append_json_list(
            INTERACTIONS_LOG,
            {
                "timestamp": utc_now(),
                "question": str(question or "")[:200],
                "answer": str(answer or "")[:300],
                "confidence": confidence,
                "data_keys": list(search_results.keys()) if isinstance(search_results, dict) else [],
                "has_data": len(search_results) > 1 if isinstance(search_results, dict) else False,
            },
            max_items=100,
        )
        sync_training_manifest()
    except Exception:
        pass


def analyze_recent_interactions(count=100):
    try:
        interactions = read_json(INTERACTIONS_LOG, [])
        if not isinstance(interactions, list) or not interactions:
            return {"total": 0, "analyzed": 0, "avg_confidence": 0, "weak_areas": [], "weak_count": 0, "quality_score": "N/A"}

        recent = interactions[-max(1, int(count or 100)):]
        total_confidence = sum(float(i.get("confidence", 0) or 0) for i in recent)
        avg_confidence = total_confidence / len(recent) if recent else 0
        weak_interactions = [i for i in recent if float(i.get("confidence", 0) or 0) < 70]

        weak_areas = []
        for interaction in weak_interactions:
            question_keywords = str(interaction.get("question", "")).lower()
            if "نفق" in question_keywords or "مصروف" in question_keywords:
                weak_areas.append("expenses")
            elif "فاتورة" in question_keywords:
                weak_areas.append("invoices")
            elif "صيانة" in question_keywords:
                weak_areas.append("services")
            elif "عميل" in question_keywords or "زبون" in question_keywords:
                weak_areas.append("customers")
            elif "مخزون" in question_keywords or "منتج" in question_keywords:
                weak_areas.append("inventory")

        return {
            "total": len(interactions),
            "analyzed": len(recent),
            "avg_confidence": round(avg_confidence, 2),
            "weak_count": len(weak_interactions),
            "weak_areas": sorted(set(weak_areas)),
            "quality_score": "ممتاز" if avg_confidence >= 90 else "جيد" if avg_confidence >= 70 else "يحتاج تحسين",
        }
    except Exception as exc:
        return {"error": str(exc)}


def generate_self_audit_report():
    try:
        analysis = analyze_recent_interactions(100)
        policy = load_training_policy()
        report = {
            "generated_at": utc_now(),
            "policy_version": policy.get("policy_version", "N/A") if isinstance(policy, dict) else "N/A",
            "interactions_analysis": analysis,
            "system_health": "healthy",
            "recommendations": [],
        }

        if analysis.get("avg_confidence", 0) < 70:
            report["system_health"] = "needs_improvement"
            report["recommendations"].append("تحسين جودة البيانات المرسلة للـ AI")

        for area in analysis.get("weak_areas", []) or []:
            report["recommendations"].append(f"تحسين البحث في: {area}")

        if not analysis.get("weak_areas") and analysis.get("avg_confidence", 0) >= 90:
            report["system_health"] = "excellent"
            report["recommendations"].append("✅ الأداء ممتاز - استمر")

        write_json(SELF_AUDIT_LOG, report)
        sync_training_manifest()
        return report
    except Exception as exc:
        return {"error": str(exc)}


def load_training_policy():
    data = read_json(TRAINING_POLICY, {})
    return data if isinstance(data, dict) else {}


def check_policy_compliance(confidence, has_data):
    policy = load_training_policy()
    min_confidence = policy.get("core_rules", {}).get("confidence_threshold", {}).get("minimum", 20)

    compliance = {"passed": True, "violations": [], "allow_partial": False}

    try:
        confidence = float(confidence or 0)
    except Exception:
        confidence = 0

    if 20 <= confidence < 50:
        compliance["allow_partial"] = True
    elif confidence < min_confidence:
        compliance["passed"] = False
        compliance["violations"].append(f"Confidence {confidence}% < الحد الأدنى {min_confidence}%")

    if not has_data and confidence < 15 and policy.get("core_rules", {}).get("no_guessing", {}).get("enabled"):
        compliance["passed"] = False
        compliance["violations"].append("لا توجد بيانات كافية للإجابة")

    return compliance


def get_system_status():
    try:
        analysis = analyze_recent_interactions(100)
        policy = load_training_policy()
        manifest = sync_training_manifest()
        return {
            "timestamp": utc_now(),
            "system_name": "Azad Garage Manager AI",
            "version": policy.get("policy_version", "N/A"),
            "knowledge_cache": "loaded" if manifest.get("files", {}).get("ai_knowledge_cache.json", {}).get("exists") else "missing",
            "avg_confidence": analysis.get("avg_confidence", 0),
            "total_interactions": analysis.get("total", 0),
            "quality_score": analysis.get("quality_score", "N/A"),
            "health": analysis.get("avg_confidence", 0) >= 70,
            "manifest": manifest.get("summary", {}),
        }
    except Exception as exc:
        return {"error": str(exc)}


__all__ = [
    "log_interaction",
    "analyze_recent_interactions",
    "generate_self_audit_report",
    "load_training_policy",
    "check_policy_compliance",
    "get_system_status",
]
