"""Flask integration for AI transaction feedback."""

from __future__ import annotations

_BOUND_APPS = set()


def bind_ai_flask_feedback(app) -> bool:
    app_id = id(app)
    if app_id in _BOUND_APPS:
        return False

    from flask import flash, jsonify, redirect, request
    from AI.engine.ai_erp_transaction_guard import AITransactionBlocked

    @app.errorhandler(AITransactionBlocked)
    def _ai_transaction_blocked(error):
        try:
            from extensions import db
            db.session.rollback()
        except Exception:
            pass
        message = getattr(error, "user_message", str(error)) or "تم منع حفظ الحركة بسبب ملاحظة حرجة."
        findings = getattr(error, "findings", []) or []
        wants_json = request.path.startswith("/api/") or request.is_json or request.headers.get("X-Requested-With") == "XMLHttpRequest" or request.accept_mimetypes.best == "application/json"
        if wants_json:
            return jsonify({"success": False, "blocked": True, "message": message, "error": message, "findings": findings}), 422
        try:
            flash(message, "danger")
        except Exception:
            pass
        return redirect(request.referrer or "/")

    @app.context_processor
    def _inject_ai_transaction_helpers():
        def ai_transaction_level_class(level):
            mapping = {"danger": "alert-danger", "warning": "alert-warning", "info": "alert-info", "success": "alert-success"}
            return mapping.get(str(level or "info"), "alert-info")
        return {"ai_transaction_level_class": ai_transaction_level_class}

    _BOUND_APPS.add(app_id)
    return True


__all__ = ["bind_ai_flask_feedback"]
