import json
import time
from flask import Blueprint, Response, jsonify, render_template, request
from flask_login import login_required

import utils
from utils.performance_monitor import get_aggregates, get_entries, get_top_slowest


performance_bp = Blueprint("performance_bp", __name__, url_prefix="/system/performance")


@performance_bp.get("/", endpoint="index")
@login_required
@utils.permission_required("manage_system_health")
def performance_index():
    metric = (request.args.get("metric") or "total_ms").strip()
    limit = request.args.get("limit", 20, type=int)
    limit = min(200, max(5, limit))
    agg_by = (request.args.get("agg_by") or "endpoint").strip()
    agg_sort = (request.args.get("agg_sort") or "p95_total_ms").strip()
    window = request.args.get("window", 1000, type=int)
    window = min(5000, max(50, window))
    top = get_top_slowest(metric=metric, limit=limit)
    recent = get_entries(limit=200)
    aggregates = get_aggregates(by=agg_by, limit=limit, window=window, sort=agg_sort)
    return render_template(
        "admin/performance.html",
        metric=metric,
        limit=limit,
        top=top,
        recent=recent,
        aggregates=aggregates,
        agg_by=agg_by,
        agg_sort=agg_sort,
        window=window,
    )


@performance_bp.get("/data", endpoint="data")
@login_required
@utils.permission_required("manage_system_health")
def performance_data():
    metric = (request.args.get("metric") or "total_ms").strip()
    limit = request.args.get("limit", 20, type=int)
    limit = min(200, max(5, limit))
    agg_by = (request.args.get("agg_by") or "endpoint").strip()
    agg_sort = (request.args.get("agg_sort") or "p95_total_ms").strip()
    window = request.args.get("window", 1000, type=int)
    window = min(5000, max(50, window))
    return jsonify(
        {
            "metric": metric,
            "limit": limit,
            "top": get_top_slowest(metric=metric, limit=limit),
            "recent": get_entries(limit=200),
            "aggregates": get_aggregates(by=agg_by, limit=limit, window=window, sort=agg_sort),
        }
    )


@performance_bp.get("/snapshot", endpoint="snapshot")
@login_required
@utils.permission_required("manage_system_health")
def performance_snapshot():
    agg_by = (request.args.get("agg_by") or "endpoint").strip()
    agg_sort = (request.args.get("agg_sort") or "p95_total_ms").strip()
    window = request.args.get("window", 1000, type=int)
    window = min(5000, max(50, window))
    limit = request.args.get("limit", 50, type=int)
    limit = min(200, max(5, limit))
    payload = {
        "ts": time.time(),
        "window": window,
        "limit": limit,
        "agg_by": agg_by,
        "agg_sort": agg_sort,
        "aggregates": get_aggregates(by=agg_by, limit=limit, window=window, sort=agg_sort),
        "top_total_ms": get_top_slowest(metric="total_ms", limit=min(50, limit)),
        "recent": get_entries(limit=200),
    }
    body = json.dumps(payload, ensure_ascii=False)
    resp = Response(body, mimetype="application/json; charset=utf-8")
    resp.headers["Content-Disposition"] = f"attachment; filename=perf_snapshot_{int(payload['ts'])}.json"
    return resp
