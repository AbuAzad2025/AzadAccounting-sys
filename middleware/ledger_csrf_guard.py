from __future__ import annotations

from flask import jsonify, request

UNSAFE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}


def _token_from_request():
    token = request.headers.get("X-CSRFToken") or request.headers.get("X-CSRF-Token") or request.headers.get("X-CSRF")
    if token:
        return token
    token = request.form.get("csrf_token") or request.form.get("_csrf_token")
    if token:
        return token
    if request.is_json:
        try:
            data = request.get_json(silent=True) or {}
            if isinstance(data, dict):
                return data.get("csrf_token") or data.get("_csrf_token")
        except Exception:
            pass
    return None


def _log_block(reason: str) -> None:
    try:
        from AI.engine.ai_storage import append_json_list, utc_now
        append_json_list(
            "security_middleware_events.json",
            {"timestamp": utc_now(), "event": "ledger_csrf_blocked", "endpoint": request.endpoint, "path": request.path, "reason": str(reason)[:200]},
            max_items=1000,
        )
    except Exception:
        pass


def init_ledger_csrf_guard(app):
    if getattr(app, "_azad_ledger_csrf_guard_enabled", False):
        return

    @app.before_request
    def _protect_ledger_unsafe_requests():
        if request.method not in UNSAFE_METHODS:
            return None
        if not (request.blueprint == "ledger" or request.path.startswith("/ledger/")):
            return None
        try:
            from models import SystemSettings
            disabled = str(SystemSettings.get_setting("disable_ledger_csrf_guard", False)).strip().lower() in {"1", "true", "yes", "on"}
            if disabled:
                return None
        except Exception:
            pass
        try:
            from flask_wtf.csrf import validate_csrf
            validate_csrf(_token_from_request())
            return None
        except Exception as exc:
            _log_block(str(exc))
            return jsonify({"success": False, "error": "رمز الحماية غير صالح. حدّث الصفحة وحاول مرة أخرى."}), 400

    app._azad_ledger_csrf_guard_enabled = True


__all__ = ["init_ledger_csrf_guard"]
