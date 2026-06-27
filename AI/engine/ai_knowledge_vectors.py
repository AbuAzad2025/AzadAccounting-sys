"""Hybrid vector index: TF-IDF (local) + optional OpenAI semantic embeddings."""

from __future__ import annotations

import math
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import numpy as np

from AI.engine.ai_knowledge_ingestor import _tokenize, load_all_chunks
from AI.engine.ai_storage import data_path, read_json, write_json

INDEX_FILE = "knowledge_sources/tfidf_index.json"
EMBEDDINGS_FILE = "knowledge_sources/chunk_embeddings.npz"
MAX_VOCAB = 6000
EMBED_MODEL = "text-embedding-3-small"
EMBED_BATCH = 64
EMBED_MAX_CHARS = 6000


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _embed_client():
    try:
        from AI.engine.ai_management import get_api_key_decrypted
        from openai import OpenAI

        key = get_api_key_decrypted("openai")
        if not key:
            return None
        return OpenAI(api_key=key, timeout=60.0)
    except Exception:
        return None


def _embed_texts(client, texts: List[str]) -> List[Optional[List[float]]]:
    out: List[Optional[List[float]]] = []
    for i in range(0, len(texts), EMBED_BATCH):
        batch = [(t or "")[:EMBED_MAX_CHARS] for t in texts[i : i + EMBED_BATCH]]
        try:
            resp = client.embeddings.create(model=EMBED_MODEL, input=batch)
            out.extend([item.embedding for item in resp.data])
        except Exception:
            out.extend([None] * len(batch))
    return out


def _build_tfidf_rows(chunks: List[Dict[str, Any]]) -> tuple[List[Dict[str, Any]], Dict[str, float]]:
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
        rows.append(
            {
                "chunk_id": chunk.get("chunk_id"),
                "source_id": chunk.get("source_id"),
                "title": chunk.get("title"),
                "text": chunk.get("text"),
                "w": {t: v / norm for t, v in weights.items()},
            }
        )
    return rows, idf


def _save_embeddings(rows: List[Dict[str, Any]], client) -> int:
    emb_path = data_path(EMBEDDINGS_FILE)
    if not client or not rows:
        emb_path.unlink(missing_ok=True)
        return 0
    texts = [str(r.get("text") or "") for r in rows]
    vectors_raw = _embed_texts(client, texts)
    ids: List[str] = []
    vectors: List[List[float]] = []
    for row, vec in zip(rows, vectors_raw):
        if vec:
            ids.append(str(row["chunk_id"]))
            vectors.append(vec)
    if not vectors:
        emb_path.unlink(missing_ok=True)
        return 0
    mat = np.array(vectors, dtype=np.float32)
    norms = np.linalg.norm(mat, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    mat = mat / norms
    np.savez_compressed(emb_path, ids=np.array(ids), vectors=mat)
    return len(ids)


def rebuild_vector_index() -> Dict[str, Any]:
    chunks = load_all_chunks()
    if not chunks:
        payload = {"vocab_size": 0, "idf": {}, "rows": [], "chunk_count": 0, "embedded_count": 0, "built_at": _utc_now()}
        write_json(INDEX_FILE, payload)
        data_path(EMBEDDINGS_FILE).unlink(missing_ok=True)
        return {"success": True, "chunks": 0, "vocab_size": 0, "embedded_count": 0}

    rows, idf = _build_tfidf_rows(chunks)
    client = _embed_client()
    embedded = _save_embeddings(rows, client)
    write_json(
        INDEX_FILE,
        {
            "vocab_size": len(idf),
            "idf": idf,
            "rows": rows,
            "chunk_count": len(rows),
            "embedded_count": embedded,
            "embed_model": EMBED_MODEL if embedded else None,
            "built_at": _utc_now(),
        },
    )
    return {"success": True, "chunks": len(rows), "vocab_size": len(idf), "embedded_count": embedded}


def get_index_status() -> Dict[str, Any]:
    index = read_json(INDEX_FILE, {})
    embedded = int(index.get("embedded_count") or 0)
    return {
        "semantic_chunks": embedded,
        "semantic_model": index.get("embed_model"),
        "search_mode": "semantic+tfidf" if embedded else "tfidf",
    }


def _row_hit(row: Dict[str, Any], score: float, method: str) -> Dict[str, Any]:
    return {
        "score": round(score, 3),
        "chunk_id": row.get("chunk_id"),
        "source_id": row.get("source_id"),
        "title": row.get("title"),
        "text": row.get("text"),
        "method": method,
    }


def _semantic_search(query: str, top_k: int, min_score: float) -> List[Dict[str, Any]]:
    emb_path = data_path(EMBEDDINGS_FILE)
    if not emb_path.exists():
        return []
    client = _embed_client()
    if not client:
        return []
    q_vec = _embed_texts(client, [query])
    if not q_vec or not q_vec[0]:
        return []

    data = np.load(emb_path, allow_pickle=True)
    ids = [str(x) for x in data["ids"]]
    matrix = data["vectors"]
    q = np.array(q_vec[0], dtype=np.float32)
    q = q / (np.linalg.norm(q) or 1.0)
    scores = matrix @ q

    index = read_json(INDEX_FILE, {})
    rows_by_id = {str(r.get("chunk_id")): r for r in (index.get("rows") or []) if r.get("chunk_id")}

    ranked = sorted(zip(ids, scores), key=lambda x: float(x[1]), reverse=True)
    hits: List[Dict[str, Any]] = []
    for cid, score in ranked[: max(1, int(top_k or 8)) * 2]:
        if float(score) < min_score:
            continue
        row = rows_by_id.get(cid)
        if row:
            hits.append(_row_hit(row, float(score), "semantic"))
        if len(hits) >= top_k:
            break
    return hits


def _tfidf_search(query: str, top_k: int, min_score: float) -> List[Dict[str, Any]]:
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

    return [_row_hit(row, score, "tfidf") for score, row in scored[: max(1, int(top_k or 8))]]


def vector_search(query: str, top_k: int = 8, min_score: float = 0.04) -> List[Dict[str, Any]]:
    semantic = _semantic_search(query, top_k, max(0.32, min_score))
    if semantic:
        return semantic[:top_k]
    return _tfidf_search(query, top_k, min_score)


__all__ = ["rebuild_vector_index", "vector_search", "get_index_status"]
