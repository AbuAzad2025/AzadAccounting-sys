import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app import create_app


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def main() -> int:
    app = create_app()
    root = Path(__file__).resolve().parents[1]
    sec_dir = root / "templates" / "security"
    static_dir = root / "static"

    html_files = list(sec_dir.rglob("*.html"))

    endpoint_pat = re.compile(r"url_for\(\s*['\"]([^'\"]+)['\"]")
    static_pat = re.compile(r"url_for\(\s*['\"]static['\"]\s*,\s*filename\s*=\s*['\"]([^'\"]+)['\"]")
    static_url_pat = re.compile(r"static_url\(\s*['\"]([^'\"]+)['\"]\s*\)")
    path_pat = re.compile(r"/security/[A-Za-z0-9_\-/]+")

    endpoints: set[str] = set()
    static_refs: set[str] = set()
    sec_paths: set[str] = set()

    for p in html_files:
        txt = _read_text(p)
        endpoints.update(endpoint_pat.findall(txt))
        static_refs.update(static_pat.findall(txt))
        static_refs.update(static_url_pat.findall(txt))
        sec_paths.update(path_pat.findall(txt))

    js_dir = static_dir / "js"
    if js_dir.exists():
        for p in js_dir.glob("security*.js"):
            sec_paths.update(path_pat.findall(_read_text(p)))

    with app.app_context():
        missing_endpoints = sorted([ep for ep in endpoints if ep not in app.view_functions])
        rules = [r.rule for r in app.url_map.iter_rules()]

        def path_exists(u: str) -> bool:
            if u in rules:
                return True
            if u.endswith("/") and u[:-1] in rules:
                return True
            if (u + "/") in rules:
                return True
            pref = u.rstrip("/") + "/"
            return any(rr.startswith(pref) for rr in rules)

        missing_paths = sorted([u for u in sec_paths if not path_exists(u)])

    missing_static = []
    for fn in sorted(static_refs):
        fn2 = fn.replace("static/", "")
        if not (static_dir / fn2).exists():
            missing_static.append(fn)

    sec_py = root / "routes" / "security.py"
    rt_pat = re.compile(r"render_template\(\s*['\"](security/[^'\"]+)['\"]")
    rt = set(rt_pat.findall(_read_text(sec_py)))
    missing_templates = sorted([t for t in rt if not (root / "templates" / t).exists()])

    report = {
        "security_templates_count": len(html_files),
        "unique_url_for_endpoints": len(endpoints),
        "missing_endpoints_count": len(missing_endpoints),
        "missing_endpoints": missing_endpoints,
        "unique_static_refs": len(static_refs),
        "missing_static_count": len(missing_static),
        "missing_static": missing_static,
        "hardcoded_security_paths_count": len(sec_paths),
        "missing_security_paths_count": len(missing_paths),
        "missing_security_paths": missing_paths,
        "render_template_refs": len(rt),
        "missing_render_templates_count": len(missing_templates),
        "missing_render_templates": missing_templates,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
