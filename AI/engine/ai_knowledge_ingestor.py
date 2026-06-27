"""Ingest external knowledge files (PDF, MD, TXT, JSON, CSV) for local RAG."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from AI.engine.ai_storage import data_path, read_json, sync_training_manifest, write_json

SOURCES_INDEX = "knowledge_sources/index.json"
SOURCES_FILES_DIR = "knowledge_sources/files"
CHUNKS_DIR = "knowledge_sources/chunks"
ALLOWED_EXTENSIONS = {".pdf", ".md", ".markdown", ".txt", ".json", ".csv"}
CHUNK_SIZE = 900
CHUNK_OVERLAP = 150
MAX_FILE_BYTES = 25 * 1024 * 1024


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _ensure_dirs() -> None:
    for rel in (SOURCES_FILES_DIR, CHUNKS_DIR):
        data_path(rel).mkdir(parents=True, exist_ok=True)


def _load_index() -> Dict[str, Any]:
    data = read_json(SOURCES_INDEX, {})
    if not isinstance(data, dict):
        data = {}
    data.setdefault("sources", {})
    data.setdefault("stats", {"total_sources": 0, "total_chunks": 0})
    return data


def _save_index(index: Dict[str, Any]) -> None:
    sources = index.get("sources") if isinstance(index.get("sources"), dict) else {}
    chunks_total = sum(int(s.get("chunks_count") or 0) for s in sources.values())
    index["stats"] = {"total_sources": len(sources), "total_chunks": chunks_total, "updated_at": _utc_now()}
    write_json(SOURCES_INDEX, index)
    sync_training_manifest(extra_files=[SOURCES_INDEX])


def _safe_filename(name: str) -> str:
    base = re.sub(r"[^\w\u0600-\u06FF.\-]+", "_", str(name or "file").strip())[:120]
    return base or "file"


def _new_source_id(filename: str) -> str:
    digest = hashlib.sha1(f"{filename}{uuid.uuid4()}".encode()).hexdigest()[:10]
    return f"src_{digest}"


def _normalize_ar(text: str) -> str:
    t = str(text or "").lower()
    t = re.sub(r"[\u0617-\u061A\u064B-\u0652]", "", t)
    return re.sub("[إأٱآا]", "ا", t).replace("ى", "ي").replace("ة", "ه")


def _tokenize(text: str) -> List[str]:
    normalized = _normalize_ar(text)
    tokens = re.findall(r"[\w\u0600-\u06FF]{2,}", normalized)
    return tokens[:500]


def _chunk_text(text: str, source_id: str, title: str) -> List[Dict[str, Any]]:
    clean = str(text or "").strip()
    if not clean:
        return []
    chunks: List[Dict[str, Any]] = []
    start = 0
    idx = 0
    while start < len(clean):
        end = min(len(clean), start + CHUNK_SIZE)
        if end < len(clean):
            break_at = clean.rfind("\n", start, end)
            if break_at > start + CHUNK_SIZE // 2:
                end = break_at
        piece = clean[start:end].strip()
        if piece:
            chunks.append(
                {
                    "chunk_id": f"{source_id}_{idx}",
                    "source_id": source_id,
                    "title": title,
                    "text": piece,
                    "index": idx,
                    "tokens": _tokenize(piece),
                }
            )
            idx += 1
        if end >= len(clean):
            break
        start = max(end - CHUNK_OVERLAP, start + 1)
    return chunks


def _json_to_text(data: Any, prefix: str = "") -> str:
    lines: List[str] = []
    if isinstance(data, dict):
        for key, value in data.items():
            key_s = str(key)
            if isinstance(value, (dict, list)):
                lines.append(f"{prefix}{key_s}:")
                lines.append(_json_to_text(value, prefix=prefix + "  "))
            else:
                lines.append(f"{prefix}{key_s}: {value}")
    elif isinstance(data, list):
        for i, item in enumerate(data[:500]):
            if isinstance(item, (dict, list)):
                lines.append(f"{prefix}[{i}]")
                lines.append(_json_to_text(item, prefix=prefix + "  "))
            else:
                lines.append(f"{prefix}- {item}")
    else:
        lines.append(f"{prefix}{data}")
    return "\n".join(lines)


def _extract_text(path: Path) -> Tuple[str, str]:
    ext = path.suffix.lower()
    if ext in {".md", ".markdown", ".txt"}:
        return path.read_text(encoding="utf-8", errors="ignore")[:2_000_000], ext.lstrip(".")
    if ext == ".json":
        raw = json.loads(path.read_text(encoding="utf-8", errors="ignore"))
        return _json_to_text(raw), "json"
    if ext == ".csv":
        rows = []
        with path.open("r", encoding="utf-8", errors="ignore", newline="") as f:
            reader = csv.reader(f)
            for row in reader:
                rows.append(" | ".join(row))
        return "\n".join(rows)[:2_000_000], "csv"
    if ext == ".pdf":
        try:
            import PyPDF2
        except ImportError as exc:
            raise RuntimeError("PyPDF2 غير مثبت — pip install PyPDF2") from exc
        parts = []
        with path.open("rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages[:500]:
                parts.append((page.extract_text() or "")[:100_000])
        return "\n".join(parts)[:2_000_000], "pdf"
    raise ValueError(f"نوع غير مدعوم: {ext}")


def list_sources() -> List[Dict[str, Any]]:
    index = _load_index()
    sources = index.get("sources", {})
    rows = list(sources.values()) if isinstance(sources, dict) else []
    rows.sort(key=lambda r: r.get("uploaded_at") or "", reverse=True)
    return rows


def get_sources_summary() -> Dict[str, Any]:
    index = _load_index()
    stats = index.get("stats") if isinstance(index.get("stats"), dict) else {}
    return {
        "total_sources": int(stats.get("total_sources") or 0),
        "total_chunks": int(stats.get("total_chunks") or 0),
        "updated_at": stats.get("updated_at") or "",
        "sources": list_sources()[:20],
    }


def ingest_bytes(content: bytes, filename: str, uploaded_by: Optional[int] = None, title: Optional[str] = None) -> Dict[str, Any]:
    _ensure_dirs()
    if len(content) > MAX_FILE_BYTES:
        return {"success": False, "error": f"الملف أكبر من {MAX_FILE_BYTES // (1024*1024)}MB"}
    safe = _safe_filename(filename)
    ext = Path(safe).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        return {"success": False, "error": f"الامتداد غير مدعوم. المسموح: {', '.join(sorted(ALLOWED_EXTENSIONS))}"}

    source_id = _new_source_id(safe)
    dest = data_path(SOURCES_FILES_DIR) / f"{source_id}_{safe}"
    dest.write_bytes(content)

    try:
        text, doc_type = _extract_text(dest)
    except Exception as exc:
        dest.unlink(missing_ok=True)
        return {"success": False, "error": str(exc)}

    display_title = (title or Path(safe).stem).strip() or source_id
    chunks = _chunk_text(text, source_id, display_title)
    if not chunks:
        dest.unlink(missing_ok=True)
        return {"success": False, "error": "لم يُستخرج أي نص من الملف"}

    chunk_path = data_path(f"{CHUNKS_DIR}/{source_id}.json")
    write_json(chunk_path, {"source_id": source_id, "chunks": chunks})

    meta = {
        "source_id": source_id,
        "filename": safe,
        "title": display_title,
        "type": doc_type,
        "size_bytes": len(content),
        "text_length": len(text),
        "chunks_count": len(chunks),
        "uploaded_at": _utc_now(),
        "uploaded_by": uploaded_by,
        "status": "indexed",
        "storage_path": str(dest.name),
    }
    index = _load_index()
    index["sources"][source_id] = meta
    _save_index(index)
    sync_training_manifest(extra_files=[SOURCES_INDEX, f"{CHUNKS_DIR}/{source_id}.json"])
    _rebuild_vectors()

    try:
        from AI.engine.ai_deep_memory import get_deep_memory
        get_deep_memory().remember_concept(
            f"مصدر معرفة: {display_title}",
            f"تم فهرسة {len(chunks)} مقطع من ملف {safe} ({doc_type})",
            examples=[c["text"][:200] for c in chunks[:3]],
            related=[source_id],
        )
    except Exception:
        pass

    return {"success": True, "source": meta}


def ingest_file_path(file_path: str, title: Optional[str] = None, uploaded_by: Optional[int] = None) -> Dict[str, Any]:
    path = Path(file_path)
    if not path.exists():
        return {"success": False, "error": "الملف غير موجود"}
    return ingest_bytes(path.read_bytes(), path.name, uploaded_by=uploaded_by, title=title)


def _rebuild_vectors() -> None:
    try:
        from AI.engine.ai_knowledge_vectors import rebuild_vector_index
        rebuild_vector_index()
    except Exception:
        pass


def delete_source(source_id: str) -> Dict[str, Any]:
    index = _load_index()
    sources = index.get("sources", {})
    meta = sources.pop(source_id, None) if isinstance(sources, dict) else None
    if not meta:
        return {"success": False, "error": "المصدر غير موجود"}
    storage = meta.get("storage_path")
    if storage:
        try:
            data_path(f"{SOURCES_FILES_DIR}/{storage}").unlink(missing_ok=True)
        except Exception:
            pass
    try:
        data_path(f"{CHUNKS_DIR}/{source_id}.json").unlink(missing_ok=True)
    except Exception:
        pass
    _save_index(index)
    _rebuild_vectors()
    return {"success": True, "deleted": source_id}


def load_all_chunks() -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    index = _load_index()
    sources = index.get("sources", {}) if isinstance(index.get("sources"), dict) else {}
    for source_id in sources:
        payload = read_json(f"{CHUNKS_DIR}/{source_id}.json", {})
        if isinstance(payload, dict):
            for chunk in payload.get("chunks") or []:
                if isinstance(chunk, dict) and chunk.get("text"):
                    rows.append(chunk)
    return rows


def reindex_all() -> Dict[str, Any]:
    index = _load_index()
    sources = index.get("sources", {}) if isinstance(index.get("sources"), dict) else {}
    ok, failed = 0, []
    for source_id, meta in list(sources.items()):
        storage = meta.get("storage_path")
        if not storage:
            failed.append({"source_id": source_id, "error": "missing storage"})
            continue
        path = data_path(f"{SOURCES_FILES_DIR}/{storage}")
        if not path.exists():
            failed.append({"source_id": source_id, "error": "file missing"})
            continue
        try:
            text, _ = _extract_text(path)
            chunks = _chunk_text(text, source_id, meta.get("title") or source_id)
            write_json(f"{CHUNKS_DIR}/{source_id}.json", {"source_id": source_id, "chunks": chunks})
            meta["chunks_count"] = len(chunks)
            meta["text_length"] = len(text)
            meta["reindexed_at"] = _utc_now()
            meta["status"] = "indexed"
            sources[source_id] = meta
            ok += 1
        except Exception as exc:
            failed.append({"source_id": source_id, "error": str(exc)})
    index["sources"] = sources
    _save_index(index)
    _rebuild_vectors()
    return {"success": True, "reindexed": ok, "failed": failed}


def import_legacy_books() -> Dict[str, Any]:
    """Index books already in AI/data/books via BookReader into knowledge chunks."""
    try:
        from AI.engine.ai_book_reader import get_book_reader
        reader = get_book_reader()
        imported = 0
        for book_id, info in (reader.book_index or {}).items():
            content_file = reader.books_dir / f"{book_id}_content.txt"
            if not content_file.exists():
                continue
            source_id = f"book_{book_id}"
            index = _load_index()
            if source_id in index.get("sources", {}):
                continue
            text = content_file.read_text(encoding="utf-8", errors="ignore")
            title = info.get("title") or book_id
            chunks = _chunk_text(text, source_id, title)
            write_json(f"{CHUNKS_DIR}/{source_id}.json", {"source_id": source_id, "chunks": chunks})
            index["sources"][source_id] = {
                "source_id": source_id,
                "filename": info.get("file") or book_id,
                "title": title,
                "type": info.get("format") or "book",
                "size_bytes": info.get("size") or len(text),
                "text_length": len(text),
                "chunks_count": len(chunks),
                "uploaded_at": info.get("read_date") or _utc_now(),
                "status": "indexed",
                "origin": "legacy_book",
            }
            _save_index(index)
            imported += 1
        _rebuild_vectors()
        return {"success": True, "imported": imported}
    except Exception as exc:
        return {"success": False, "error": str(exc)}


__all__ = [
    "ALLOWED_EXTENSIONS",
    "list_sources",
    "get_sources_summary",
    "ingest_bytes",
    "ingest_file_path",
    "delete_source",
    "load_all_chunks",
    "reindex_all",
    "import_legacy_books",
]
