from __future__ import annotations

import os
from datetime import datetime, timezone

from sqlalchemy import text

from extensions import db


def get_live_metrics_json() -> dict:
    now = datetime.now(timezone.utc)

    db_up = 0
    try:
        db.session.execute(text("SELECT 1")).scalar()
        db_up = 1
    except Exception:
        db_up = 0

    process_metrics = {}
    system_metrics = {}
    try:
        import psutil

        process = psutil.Process()
        process_metrics = {
            "memory_rss_mb": round(process.memory_info().rss / (1024**2), 2),
            "memory_percent": round(process.memory_percent(), 2),
            "cpu_percent": round(process.cpu_percent(interval=0.0), 2),
            "num_threads": int(process.num_threads()),
            "create_time": datetime.fromtimestamp(process.create_time(), tz=timezone.utc).isoformat(),
        }
        system_metrics = {
            "cpu_count": os.cpu_count(),
            "cpu_percent": float(psutil.cpu_percent(interval=0.0)),
            "memory_total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
            "memory_available_gb": round(psutil.virtual_memory().available / (1024**3), 2),
            "memory_percent": float(psutil.virtual_memory().percent),
        }
    except Exception:
        process_metrics = {}
        system_metrics = {}

    return {
        "timestamp": now.isoformat(),
        "db_up": db_up,
        "process": process_metrics,
        "system": system_metrics,
    }

