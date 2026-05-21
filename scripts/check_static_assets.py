import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STATIC_DIR = ROOT / "static"
TEMPLATES_DIR = ROOT / "templates"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def _exists_static(rel: str) -> bool:
    s = (rel or "").strip().replace("\\", "/")
    if not s:
        return True
    if s.startswith(("http://", "https://", "//", "data:")):
        return True
    s = s.lstrip("/")
    if s.startswith("static/"):
        s = s[len("static/") :]
    return (STATIC_DIR / s).exists()


def main() -> int:
    url_for_static = re.compile(
        r"url_for\(\s*['\"]static['\"]\s*,\s*filename\s*=\s*(['\"])([^'\"]+)\1"
    )
    static_url_pat = re.compile(r"static_url\(\s*(['\"])([^'\"]+)\1\s*\)")
    hardcoded_static_pat = re.compile(r"(?<![A-Za-z0-9_])(/static/[A-Za-z0-9_\-./]+)")

    refs = {}
    for p in TEMPLATES_DIR.rglob("*.html"):
        txt = _read_text(p)
        for _, fn in url_for_static.findall(txt):
            refs.setdefault(fn, []).append(str(p.relative_to(ROOT)))
        for _, fn in static_url_pat.findall(txt):
            refs.setdefault(fn, []).append(str(p.relative_to(ROOT)))
        for fn in hardcoded_static_pat.findall(txt):
            refs.setdefault(fn, []).append(str(p.relative_to(ROOT)))

    for p in (STATIC_DIR / "js").rglob("*.js"):
        txt = _read_text(p)
        for fn in hardcoded_static_pat.findall(txt):
            refs.setdefault(fn, []).append(str(p.relative_to(ROOT)))

    missing = sorted([k for k in refs.keys() if not _exists_static(k)])
    report = {
        "unique_static_refs": len(refs),
        "missing_static_count": len(missing),
        "missing_static": missing,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

