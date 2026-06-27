"""Lightweight TF-IDF vector index for hybrid RAG (numpy only, no extra ML deps)."""

from __future__ import annotations

import math
from datetime import datetime, timezone
from typing import Any, Dict, List

from AI.engine.ai_knowledge_ingestor import _tokenize, load_all_chunks
from AI.engine.ai_storage import read_json, write_json

INDEX_FILE = "knowledge_sources/tfidf_index.json"
MAX_VOCAB = 6000


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def rebuild_vector_index() -> Dict[str, Any]:
    chunks = load_all_chunks()
    if not chunks:
        payload = {"vocab_size": 0, "idf": {}, "rows": [], "chunk_count": 0, "built_at": _utc_now()}
        write_json(INDEX_FILE, payload)
        return {"success": True, "chunks": 0, "vocab_size": 0}

    doc_tokens = [_tokenize(str(c.get("text") or "")) for c in chunks]
    df: Dict[str, int] = {}
    for tokens in doc_tokens:
        for token in set(tokens):
            df[token] = df.get(token, 0) + 1

    n_docs = len(chunks)
    vocab_items = sorted(df.items(), key=lambda x: (-x[1], x[0]))[:MAX_VOCAB]
    idf = {token: math.log((n_docs + 1) / (count + 1)) + 1.0 for token, count in vocab_items}

    rows: List[Dict[str, Any]] = []
    for chunk, tokens in zip(chunks, doc_tokens):
        tf: Dict[str, int] = {}
        for token in tokens:
            if token in idf:
                tf[token] = tf.get(token, 0) + 1
        if not tf:
            continue
        denom = max(len(tokens), 1)
        weights = {t: (c / denom) * idf[t] for t, c in tf.items()}
        norm = math.sqrt(sum(v * v for v in weights.values())) or 1.0
        weights = {t: v / norm for t, v in weights.items()}
        rows.append(
            {
                "chunk_id": chunk.get("chunk_id"),
                "source_id": chunk.get("source_id"),
                "title": chunk.get("title"),
                "text": chunk.get("text"),
                "w": weights,
            }
        )

    write_json(
        INDEX_FILE,
        {"vocab_size": len(idf), "idf": idf, "rows": rows, "chunk_count": len(rows), "built_at": _utc_now()},
    )
    return {"success": True, "chunks": len(rows), "vocab_size": len(idf)}


def vector_search(query: str, top_k: int = 8, min_score: float = 0.04) -> List[Dict[str, Any]]:
    index = read_json(INDEX_FILE, {})
    rows = index.get("rows") if isinstance(index.get("rows"), list) else []
    idf = index.get("idf") if isinstance(index.get("idf"), dict) else {}
    if not rows or not idf:
        return []

    q_tokens = _tokenize(query)
    if not q_tokens:
        return []

    tf: Dict[str, int] = {}
    for token in q_tokens:
        if token in idf:
            tf[token] = tf.get(token, 0) + 1
    if not tf:
        return []

    denom = max(len(q_tokens), 1)
    q_weights = {t: (c / denom) * idf[t] for t, c in tf.items()}
    q_norm = math.sqrt(sum(v * v for v in q_weights.values())) or 1.0
    q_weights = {t: v / q_norm for t, v in q_weights.items()}

    scored: List[tuple] = []
    for row in rows:
        weights = row.get("w") if isinstance(row.get("w"), dict) else {}
        score = sum(q_weights.get(t, 0.0) * weights.get(t, 0.0) for t in q_weights if t in weights)
        if score >= min_score:
            scored.append((score, row))
    scored.sort(key=lambda x: x[0], reverse=True)

    results: List[Dict[str, Any]] = []
    for score, row in scored[: max(1, int(top_k or 8))]:
        results.append(
            {
                "score": round(score, 3),
                "chunk_id": row.get("chunk_id"),
                "source_id": row.get("source_id"),
                "title": row.get("title"),
                "text": row.get("text"),
                "method": "vector",
            }
        )
    return results


__all__ = ["rebuild_vector_index", "vector_search"]
