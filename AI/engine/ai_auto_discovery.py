"""AI system auto-discovery.

Builds a lightweight map of Flask routes and templates so the assistant can
answer navigation questions. Public function names are kept stable.
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from flask import current_app

SYSTEM_MAP_FILE = "AI/data/ai_system_map.json"
DISCOVERY_LOG_FILE = "AI/data/ai_discovery_log.json"
DISCOVERY_MAX_AGE_HOURS = 24

ROUTE_SYNONYMS = {
    "صيانة": ["service", "repair", "maintenance"],
    "عملاء": ["customers", "customer", "client"],
    "عميل": ["customers", "customer", "client"],
    "مبيعات": ["sales", "sale", "invoice"],
    "نفقات": ["expenses", "expense"],
    "مصروف": ["expenses", "expense"],
    "موردين": ["vendors", "vendor", "supplier", "partner"],
    "مورد": ["vendors", "vendor", "supplier"],
    "مخازن": ["warehouses", "warehouse", "stock"],
    "مخزن": ["warehouses", "warehouse", "stock"],
    "منتجات": ["products", "product", "parts", "part"],
    "منتج": ["products", "product", "parts", "part"],
    "دفتر": ["ledger", "account"],
    "تقارير": ["reports", "report"],
    "تقرير": ["reports", "report"],
    "مستخدمين": ["users", "user"],
    "مستخدم": ["users", "user"],
    "أدوار": ["roles", "role", "permission", "permissions"],
    "ادوار": ["roles", "role", "permission", "permissions"],
    "أمان": ["security", "auth"],
    "امان": ["security", "auth"],
    "متجر": ["shop", "catalog"],
    "دفعات": ["payments", "payment"],
    "دفع": ["payments", "payment"],
    "شيكات": ["checks", "check"],
    "شحن": ["shipments", "shipment"],
    "شريك": ["partners", "partner"],
}


def _ensure_data_dir() -> None:
    os.makedirs("AI/data", exist_ok=True)


def _read_json(path: str, default: Any) -> Any:
    try:
        if not os.path.exists(path):
            return default
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def _write_json(path: str, data: Any) -> None:
    _ensure_data_dir()
    tmp_path = f"{path}.tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp_path, path)


def discover_all_routes() -> List[Dict[str, Any]]:
    routes: List[Dict[str, Any]] = []
    try:
        for rule in current_app.url_map.iter_rules():
            if rule.endpoint == "static":
                continue
            blueprint = rule.endpoint.split(".")[0] if "." in rule.endpoint else None
            function_name = rule.endpoint.split(".")[-1]
            routes.append({
                "endpoint": rule.endpoint,
                "url": str(rule.rule),
                "methods": sorted(list(rule.methods - {"HEAD", "OPTIONS"})),
                "blueprint": blueprint,
                "function_name": function_name,
            })
    except Exception:
        return []
    return routes


def discover_all_templates() -> List[Dict[str, Any]]:
    templates: List[Dict[str, Any]] = []
    templates_dir = Path("templates")
    if not templates_dir.exists():
        return templates
    try:
        for template_file in templates_dir.rglob("*.html"):
            relative = template_file.relative_to(templates_dir)
            stat = template_file.stat()
            templates.append({
                "name": str(relative),
                "full_path": str(template_file),
                "module": str(relative.parent) if relative.parent != Path(".") else "root",
                "file_size": stat.st_size,
                "last_modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            })
    except Exception:
        return templates
    return templates


def link_routes_to_templates(routes: List[Dict[str, Any]], templates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    template_names = {t.get("name") for t in templates}
    linked: List[Dict[str, Any]] = []
    for route in routes:
        item = dict(route)
        blueprint = route.get("blueprint") or ""
        function = route.get("function_name") or ""
        candidates: List[str] = []
        if blueprint:
            guesses = [f"{blueprint}/{function}.html"]
            if function == "index":
                guesses.append(f"{blueprint}/index.html")
            for common in ("list", "detail", "edit", "create", "delete", "view", "show", "new"):
                if common in function:
                    guesses.append(f"{blueprint}/{common}.html")
            for guess in guesses:
                if guess in template_names and guess not in candidates:
                    candidates.append(guess)
        item["linked_templates"] = candidates
        item["has_template"] = bool(candidates)
        linked.append(item)
    return linked


def categorize_routes(routes: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    categories: Dict[str, List[Dict[str, Any]]] = {"api": [], "admin": [], "security": [], "reports": [], "public": [], "other": []}
    for route in routes:
        url = str(route.get("url") or "").lower()
        blueprint = str(route.get("blueprint") or "").lower()
        if "/api/" in url or blueprint == "api":
            categories["api"].append(route)
        elif "/security" in url or blueprint in {"security", "security_control"}:
            categories["security"].append(route)
        elif "/report" in url or blueprint in {"reports", "admin_reports", "financial_reports"}:
            categories["reports"].append(route)
        elif "/auth/" in url or blueprint in {"auth", "shop"}:
            categories["public"].append(route)
        elif "/admin/" in url or "admin" in blueprint:
            categories["admin"].append(route)
        else:
            categories["other"].append(route)
    return categories


def build_system_map() -> Dict[str, Any]:
    routes = discover_all_routes()
    templates = discover_all_templates()
    linked_routes = link_routes_to_templates(routes, templates)
    linked_count = sum(1 for route in linked_routes if route.get("has_template"))
    system_map = {
        "generated_at": datetime.now().isoformat(),
        "system_name": "نظام أزاد لإدارة الكراج",
        "version": "4.0.0",
        "statistics": {
            "total_routes": len(routes),
            "total_templates": len(templates),
            "linked_routes": linked_count,
            "unlinked_routes": len(routes) - linked_count,
        },
        "routes": {"all": linked_routes, "by_category": categorize_routes(linked_routes)},
        "templates": {"all": templates, "by_module": group_templates_by_module(templates)},
        "blueprints": extract_blueprints(routes),
        "modules": extract_modules(templates),
    }
    save_system_map(system_map)
    log_discovery_event("auto_build", len(routes), len(templates))
    return system_map


def group_templates_by_module(templates: List[Dict[str, Any]]) -> Dict[str, List[str]]:
    grouped: Dict[str, List[str]] = {}
    for template in templates:
        grouped.setdefault(template.get("module") or "root", []).append(template.get("name"))
    return grouped


def extract_blueprints(routes: List[Dict[str, Any]]) -> List[str]:
    return sorted({route.get("blueprint") for route in routes if route.get("blueprint")})


def extract_modules(templates: List[Dict[str, Any]]) -> List[str]:
    return sorted({template.get("module") for template in templates if template.get("module") and template.get("module") != "root"})


def save_system_map(system_map: Dict[str, Any]) -> None:
    try:
        _write_json(SYSTEM_MAP_FILE, system_map)
    except Exception:
        pass


def load_system_map() -> Optional[Dict[str, Any]]:
    data = _read_json(SYSTEM_MAP_FILE, None)
    return data if isinstance(data, dict) else None


def log_discovery_event(event_type: str, routes_count: int, templates_count: int) -> None:
    try:
        logs = _read_json(DISCOVERY_LOG_FILE, [])
        if not isinstance(logs, list):
            logs = []
        logs.append({
            "timestamp": datetime.now().isoformat(),
            "event": event_type,
            "routes_discovered": routes_count,
            "templates_discovered": templates_count,
        })
        _write_json(DISCOVERY_LOG_FILE, logs[-50:])
    except Exception:
        pass


def _search_terms(keyword: str) -> List[str]:
    text = str(keyword or "").lower()
    terms = {text}
    for ar_word, synonyms in ROUTE_SYNONYMS.items():
        if ar_word.lower() in text:
            terms.update(synonyms)
        if any(syn in text for syn in synonyms):
            terms.add(ar_word.lower())
            terms.update(synonyms)
    return [term for term in terms if term]


def find_route_by_keyword(keyword: str, system_map: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    system_map = system_map or load_system_map()
    if not system_map or not system_map.get("routes"):
        return {"matches": [], "keyword": keyword, "total": 0}

    matches: List[Dict[str, Any]] = []
    terms = _search_terms(keyword)
    for route in system_map.get("routes", {}).get("all", []):
        endpoint = str(route.get("endpoint") or "").lower()
        url = str(route.get("url") or "").lower()
        blueprint = str(route.get("blueprint") or "").lower()
        templates = [str(t).lower() for t in route.get("linked_templates", [])]
        score = 0
        for term in terms:
            if term in endpoint:
                score += 10
            if term in url:
                score += 8
            if term in blueprint:
                score += 6
            if any(term in tpl for tpl in templates):
                score += 4
        if score > 0:
            item = dict(route)
            item["relevance_score"] = score
            matches.append(item)
    matches.sort(key=lambda item: item.get("relevance_score", 0), reverse=True)
    return {"matches": matches[:10], "keyword": keyword, "total": len(matches)}


def find_template_by_keyword(keyword: str, system_map: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    system_map = system_map or load_system_map()
    if not system_map:
        return []
    text = str(keyword or "").lower()
    return [template for template in system_map.get("templates", {}).get("all", []) if text in str(template.get("name") or "").lower()]


def get_route_suggestions(user_query: str) -> Optional[Dict[str, Any]]:
    system_map = load_system_map()
    if not system_map:
        return None

    query = str(user_query or "").lower()
    for arabic, english_terms in ROUTE_SYNONYMS.items():
        if arabic.lower() in query or any(term in query for term in english_terms):
            result = find_route_by_keyword(english_terms[0], system_map)
            return {"keyword": arabic, "matches": result.get("matches", [])[:5], "count": result.get("total", 0)}

    result = find_route_by_keyword(user_query, system_map)
    if result.get("matches"):
        return {"keyword": user_query, "matches": result.get("matches", [])[:5], "count": result.get("total", 0)}
    return None


def auto_discover_if_needed() -> Optional[Dict[str, Any]]:
    if not os.path.exists(SYSTEM_MAP_FILE):
        return build_system_map()
    try:
        age_hours = (datetime.now().timestamp() - os.path.getmtime(SYSTEM_MAP_FILE)) / 3600
        if age_hours > DISCOVERY_MAX_AGE_HOURS:
            return build_system_map()
    except Exception:
        pass
    return load_system_map()


__all__ = [
    "SYSTEM_MAP_FILE",
    "DISCOVERY_LOG_FILE",
    "discover_all_routes",
    "discover_all_templates",
    "link_routes_to_templates",
    "categorize_routes",
    "build_system_map",
    "group_templates_by_module",
    "extract_blueprints",
    "extract_modules",
    "save_system_map",
    "load_system_map",
    "log_discovery_event",
    "find_route_by_keyword",
    "find_template_by_keyword",
    "get_route_suggestions",
    "auto_discover_if_needed",
]
