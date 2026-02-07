import threading
import time
import json
import os
from collections import deque
from typing import Any, Dict, List, Optional

from flask import g, has_request_context, request
from flask.signals import before_render_template, template_rendered
from sqlalchemy import event
from sqlalchemy.engine import Engine


_STORE_LOCK = threading.Lock()
_STORE: deque = deque(maxlen=1000)
_SQL_LISTENERS_LOCK = threading.Lock()
_SQL_LISTENERS_REGISTERED = False


def _is_enabled(app=None) -> bool:
    try:
        if app is None:
            from flask import current_app
            app = current_app
        return bool(app.config.get("PERF_MONITOR_ENABLED", False))
    except Exception:
        return False


def _should_track_request() -> bool:
    try:
        if not has_request_context():
            return False
        if request.path.startswith(("/static/", "/favicon.ico", "/socket.io")):
            return False
        return True
    except Exception:
        return False


def _perf_now() -> float:
    return time.perf_counter()


def _before_render(sender, template, context, **extra):
    if not _should_track_request():
        return
    if not _is_enabled(sender):
        return
    try:
        g._perf_template_start = _perf_now()
    except Exception:
        pass


def _after_render(sender, template, context, **extra):
    if not _should_track_request():
        return
    if not _is_enabled(sender):
        return
    start = getattr(g, "_perf_template_start", None)
    if start is None:
        return
    try:
        delta_ms = (_perf_now() - float(start)) * 1000
        g._perf_template_ms = float(getattr(g, "_perf_template_ms", 0.0) or 0.0) + float(delta_ms)
    except Exception:
        pass


def _before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    if not _should_track_request():
        return
    if not _is_enabled():
        return
    try:
        context._perf_query_start = _perf_now()
    except Exception:
        pass


def _after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    if not _should_track_request():
        return
    if not _is_enabled():
        return
    start = getattr(context, "_perf_query_start", None)
    if start is None:
        return
    try:
        delta_ms = (_perf_now() - float(start)) * 1000
        g._perf_sql_count = int(getattr(g, "_perf_sql_count", 0) or 0) + 1
        g._perf_sql_ms = float(getattr(g, "_perf_sql_ms", 0.0) or 0.0) + float(delta_ms)
    except Exception:
        pass


def push_entry(entry: Dict[str, Any]) -> None:
    with _STORE_LOCK:
        _STORE.append(entry)
        try:
            from flask import current_app
            path = current_app.config.get("PERF_MONITOR_PERSIST_PATH") or ""
        except Exception:
            path = ""
        path = str(path or "").strip()
        if path:
            try:
                os.makedirs(os.path.dirname(path), exist_ok=True)
            except Exception:
                pass
            try:
                with open(path, "a", encoding="utf-8") as f:
                    f.write(json.dumps(entry, ensure_ascii=False) + "\n")
            except Exception:
                pass


def get_entries(limit: int = 200) -> List[Dict[str, Any]]:
    limit = min(1000, max(1, int(limit or 200)))
    with _STORE_LOCK:
        data = list(_STORE)
    return data[-limit:][::-1]


def get_top_slowest(metric: str = "total_ms", limit: int = 20) -> List[Dict[str, Any]]:
    limit = min(200, max(1, int(limit or 20)))
    with _STORE_LOCK:
        rows = list(_STORE)
    key = str(metric or "total_ms")
    def _v(r):
        try:
            return float(r.get(key, 0) or 0)
        except Exception:
            return 0.0
    rows.sort(key=_v, reverse=True)
    return rows[:limit]


def _safe_float(v) -> float:
    try:
        return float(v or 0)
    except Exception:
        return 0.0


def _percentile(values: List[float], p: float) -> float:
    if not values:
        return 0.0
    vals = sorted(values)
    if p <= 0:
        return float(vals[0])
    if p >= 100:
        return float(vals[-1])
    k = (len(vals) - 1) * (p / 100.0)
    f = int(k)
    c = min(f + 1, len(vals) - 1)
    if f == c:
        return float(vals[f])
    d0 = vals[f] * (c - k)
    d1 = vals[c] * (k - f)
    return float(d0 + d1)


def classify_aggregate(row: Dict[str, Any]) -> str:
    total = _safe_float(row.get("avg_total_ms"))
    if total <= 0:
        return "unknown"
    sql = _safe_float(row.get("avg_sql_ms"))
    tpl = _safe_float(row.get("avg_template_ms"))
    q = _safe_float(row.get("avg_sql_count"))
    sql_ratio = sql / total if total else 0.0
    tpl_ratio = tpl / total if total else 0.0

    if q >= 50 and sql_ratio >= 0.25:
        return "db_n_plus_1"
    if sql_ratio >= 0.6:
        return "db_heavy"
    if tpl_ratio >= 0.6:
        return "template_heavy"
    if total >= 800 and sql_ratio <= 0.15 and tpl_ratio <= 0.15:
        return "python_heavy"
    if total >= 400 and (sql_ratio >= 0.25 or tpl_ratio >= 0.25):
        return "mixed"
    return "ok"


def get_aggregates(
    *,
    by: str = "endpoint",
    limit: int = 50,
    window: int = 1000,
    sort: str = "p95_total_ms",
) -> List[Dict[str, Any]]:
    limit = min(200, max(1, int(limit or 50)))
    window = min(5000, max(50, int(window or 1000)))
    with _STORE_LOCK:
        rows = list(_STORE)[-window:]

    key_field = "endpoint" if (by or "endpoint").strip() == "endpoint" else "path"
    groups: Dict[str, List[Dict[str, Any]]] = {}
    for r in rows:
        k = (r.get(key_field) or "").strip()
        if not k:
            k = "(unknown)"
        groups.setdefault(k, []).append(r)

    out: List[Dict[str, Any]] = []
    for k, items in groups.items():
        totals = [_safe_float(x.get("total_ms")) for x in items]
        sqls = [_safe_float(x.get("sql_ms")) for x in items]
        tpls = [_safe_float(x.get("template_ms")) for x in items]
        qcnt = [_safe_float(x.get("sql_count")) for x in items]
        codes = [int(x.get("status") or 0) for x in items]
        err = sum(1 for c in codes if c >= 500)
        count = len(items)
        row = {
            "key": k,
            "by": key_field,
            "count": count,
            "err_5xx": err,
            "avg_total_ms": round(sum(totals) / count, 2) if count else 0.0,
            "p95_total_ms": round(_percentile(totals, 95), 2),
            "max_total_ms": round(max(totals) if totals else 0.0, 2),
            "avg_sql_ms": round(sum(sqls) / count, 2) if count else 0.0,
            "p95_sql_ms": round(_percentile(sqls, 95), 2),
            "avg_sql_count": round(sum(qcnt) / count, 2) if count else 0.0,
            "p95_sql_count": round(_percentile(qcnt, 95), 2),
            "avg_template_ms": round(sum(tpls) / count, 2) if count else 0.0,
            "p95_template_ms": round(_percentile(tpls, 95), 2),
        }
        row["class"] = classify_aggregate(row)
        out.append(row)

    sort_key = (sort or "p95_total_ms").strip()
    def _s(r):
        return _safe_float(r.get(sort_key))
    out.sort(key=_s, reverse=True)
    return out[:limit]


def init_perf_monitor(app) -> None:
    if getattr(app, "extensions", None) is None:
        app.extensions = {}
    if app.extensions.get("perf_monitor_initialized"):
        return
    app.extensions["perf_monitor_initialized"] = True

    app.config.setdefault("PERF_MONITOR_ENABLED", bool(app.config.get("DEBUG", False)))
    app.config.setdefault("PERF_MONITOR_PERSIST_PATH", "")

    before_render_template.connect(_before_render, app)
    template_rendered.connect(_after_render, app)

    global _SQL_LISTENERS_REGISTERED
    with _SQL_LISTENERS_LOCK:
        if not _SQL_LISTENERS_REGISTERED:
            event.listen(Engine, "before_cursor_execute", _before_cursor_execute)
            event.listen(Engine, "after_cursor_execute", _after_cursor_execute)
            _SQL_LISTENERS_REGISTERED = True

    @app.after_request
    def _perf_after_request(resp):
        try:
            if not _should_track_request():
                return resp
            if not _is_enabled(app):
                return resp
            start = getattr(g, "request_start", None) or getattr(g, "_perf_request_start", None)
            if start is None:
                return resp
            total_ms = (_perf_now() - float(start)) * 1000
            entry = {
                "ts": time.time(),
                "method": request.method,
                "path": request.path,
                "endpoint": request.endpoint or "",
                "status": int(getattr(resp, "status_code", 0) or 0),
                "total_ms": round(float(total_ms), 2),
                "sql_ms": round(float(getattr(g, "_perf_sql_ms", 0.0) or 0.0), 2),
                "sql_count": int(getattr(g, "_perf_sql_count", 0) or 0),
                "template_ms": round(float(getattr(g, "_perf_template_ms", 0.0) or 0.0), 2),
            }
            try:
                if getattr(getattr(g, "microcache_key", None), "__class__", None) is not None and resp.headers.get("X-Microcache") == "HIT":
                    entry["microcache"] = "HIT"
                elif getattr(g, "microcache_key", None):
                    entry["microcache"] = resp.headers.get("X-Microcache") or "MISS"
            except Exception:
                pass
            push_entry(entry)
            if request.args.get("perf") == "1":
                resp.headers["X-Perf-Total-Ms"] = str(entry["total_ms"])
                resp.headers["X-Perf-SQL-Ms"] = str(entry["sql_ms"])
                resp.headers["X-Perf-SQL-Count"] = str(entry["sql_count"])
                resp.headers["X-Perf-Template-Ms"] = str(entry["template_ms"])
        except Exception:
            pass
        return resp
