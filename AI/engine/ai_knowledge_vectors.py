"""Hybrid vector index: local LSA semantics (sklearn) + TF-IDF + optional OpenAI boost."""

from __future__ import annotations

import math
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import joblib
import numpy as np
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import Normalizer

from AI.engine.ai_knowledge_ingestor import _normalize_ar, _tokenize, load_all_chunks
from AI.engine.ai_storage import data_path, read_json, write_json

INDEX_FILE = "knowledge_sources/tfidf_index.json"
LOCAL_EMBEDDINGS_FILE = "knowledge_sources/local_embeddings.npz"
LOCAL_LSA_PIPELINE = "knowledge_sources/lsa_pipeline.joblib"
OPENAI_EMBEDDINGS_FILE = "knowledge_sources/openai_embeddings.npz"
MAX_VOCAB = 6000
LOCAL_EMBED_MODEL = "sklearn-lsa-multilingual"
OPENAI_EMBED_MODEL = "text-embedding-3-small"
EMBED_BATCH = 32
EMBED_MAX_CHARS = 6000
LSA_DIMS = 128


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _prep_text(text: str) -> str:
    tokens = _tokenize(str(text or ""))
    return " ".join(tokens) if tokens else _normalize_ar(text)


def _build_lsa_pipeline() -> Pipeline:
    return Pipeline(
        [
            (
                "tfidf",
                TfidfVectorizer(
                    max_features=10000,
                    ngram_range=(1, 2),
                    sublinear_tf=True,
                    min_df=1,
                ),
            ),
            ("svd", TruncatedSVD(n_components=LSA_DIMS, random_state=42)),
            ("norm", Normalizer(copy=False)),
        ]
    )


def _normalize_matrix(vectors: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return vectors / norms


def _openai_client():
    try:
        from AI.engine.ai_management import get_api_key_decrypted
        from openai import OpenAI

        key = get_api_key_decrypted("openai")
        return OpenAI(api_key=key, timeout=60.0) if key else None
    except Exception:
        return None


def _openai_embed(client, texts: List[str]) -> List[Optional[List[float]]]:
    out: List[Optional[List[float]]] = []
    for i in range(0, len(texts), EMBED_BATCH):
        batch = [(t or "")[:EMBED_MAX_CHARS] for t in texts[i : i + EMBED_BATCH]]
        try:
            resp = client.embeddings.create(model=OPENAI_EMBED_MODEL, input=batch)
            out.extend([item.embedding for item in resp.data])
        except Exception:
            out.extend([None] * len(batch))
    return out


def _save_npz(path_key: str, rows: List[Dict[str, Any]], vectors: np.ndarray) -> int:
    path = data_path(path_key)
    if vectors.size == 0 or not rows:
        path.unlink(missing_ok=True)
        return 0
    ids = np.array([str(r["chunk_id"]) for r in rows[: len(vectors)]])
    np.savez_compressed(path, ids=ids, vectors=_normalize_matrix(vectors))
    return len(ids)


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


def _build_local_semantic(rows: List[Dict[str, Any]]) -> int:
    if not rows:
        data_path(LOCAL_EMBEDDINGS_FILE).unlink(missing_ok=True)
        data_path(LOCAL_LSA_PIPELINE).unlink(missing_ok=True)
        return 0
    corpus = [_prep_text(r.get("text")) for r in rows]
    if not any(corpus):
        return 0
    try:
        n_docs = len(rows)
        if n_docs == 1:
            vectorizer = TfidfVectorizer(max_features=1000, ngram_range=(1, 2), sublinear_tf=True)
            vectors = Normalizer().fit_transform(vectorizer.fit_transform(corpus).toarray())
            joblib.dump({"mode": "single", "vectorizer": vectorizer}, data_path(LOCAL_LSA_PIPELINE))
        else:
            n_comp = min(LSA_DIMS, n_docs - 1)
            pipeline = _build_lsa_pipeline()
            pipeline.set_params(svd__n_components=n_comp)
            vectors = pipeline.fit_transform(corpus)
            joblib.dump({"mode": "lsa", "pipeline": pipeline}, data_path(LOCAL_LSA_PIPELINE))
        return _save_npz(LOCAL_EMBEDDINGS_FILE, rows, np.asarray(vectors, dtype=np.float32))
    except Exception:
        return 0


def rebuild_vector_index() -> Dict[str, Any]:
    chunks = load_all_chunks()
    if not chunks:
        payload = {
            "vocab_size": 0,
            "idf": {},
            "rows": [],
            "chunk_count": 0,
            "local_embedded": 0,
            "openai_embedded": 0,
            "built_at": _utc_now(),
        }
        write_json(INDEX_FILE, payload)
        for f in (LOCAL_EMBEDDINGS_FILE, OPENAI_EMBEDDINGS_FILE, LOCAL_LSA_PIPELINE):
            data_path(f).unlink(missing_ok=True)
        return {"success": True, "chunks": 0, "local_embedded": 0, "openai_embedded": 0}

    rows, idf = _build_tfidf_rows(chunks)
    texts = [str(r.get("text") or "") for r in rows]
    local_count = _build_local_semantic(rows)

    openai_count = 0
    client = _openai_client()
    if client:
        try:
            raw = _openai_embed(client, texts)
            o_rows, o_vecs = [], []
            for row, vec in zip(rows, raw):
                if vec:
                    o_rows.append(row)
                    o_vecs.append(vec)
            if o_vecs:
                openai_count = _save_npz(OPENAI_EMBEDDINGS_FILE, o_rows, np.array(o_vecs, dtype=np.float32))
        except Exception:
            data_path(OPENAI_EMBEDDINGS_FILE).unlink(missing_ok=True)

    write_json(
        INDEX_FILE,
        {
            "vocab_size": len(idf),
            "idf": idf,
            "rows": rows,
            "chunk_count": len(rows),
            "local_embedded": local_count,
            "openai_embedded": openai_count,
            "local_model": LOCAL_EMBED_MODEL if local_count else None,
            "openai_model": OPENAI_EMBED_MODEL if openai_count else None,
            "built_at": _utc_now(),
        },
    )
    return {
        "success": True,
        "chunks": len(rows),
        "vocab_size": len(idf),
        "local_embedded": local_count,
        "openai_embedded": openai_count,
    }


def get_index_status() -> Dict[str, Any]:
    index = read_json(INDEX_FILE, {})
    local_n = int(index.get("local_embedded") or 0)
    openai_n = int(index.get("openai_embedded") or 0)
    if local_n:
        mode = "local+openai+tfidf" if openai_n else "local+tfidf"
    elif openai_n:
        mode = "openai+tfidf"
    else:
        mode = "tfidf"
    pipeline_parts = ["keyword"]
    if local_n:
        pipeline_parts.append("LSA-local")
    pipeline_parts.append("TF-IDF")
    if openai_n:
        pipeline_parts.append("OpenAI")
    return {
        "semantic_chunks": local_n or openai_n,
        "local_semantic_chunks": local_n,
        "openai_semantic_chunks": openai_n,
        "semantic_model": index.get("local_model") or index.get("openai_model"),
        "search_mode": mode,
        "search_pipeline": " → ".join(pipeline_parts),
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


def _rows_by_id() -> Dict[str, Dict[str, Any]]:
    index = read_json(INDEX_FILE, {})
    return {str(r.get("chunk_id")): r for r in (index.get("rows") or []) if r.get("chunk_id")}


def _search_npz(path_key: str, query_vec: np.ndarray, top_k: int, min_score: float, method: str) -> List[Dict[str, Any]]:
    path = data_path(path_key)
    if not path.exists():
        return []
    data = np.load(path, allow_pickle=True)
    ids = [str(x) for x in data["ids"]]
    matrix = data["vectors"]
    q = query_vec / (np.linalg.norm(query_vec) or 1.0)
    scores = matrix @ q
    lookup = _rows_by_id()
    ranked = sorted(zip(ids, scores), key=lambda x: float(x[1]), reverse=True)
    hits: List[Dict[str, Any]] = []
    for cid, score in ranked:
        if float(score) < min_score:
            break
        row = lookup.get(cid)
        if row:
            hits.append(_row_hit(row, float(score), method))
        if len(hits) >= top_k:
            break
    return hits


def _local_semantic_search(query: str, top_k: int, min_score: float) -> List[Dict[str, Any]]:
    pipe_path = data_path(LOCAL_LSA_PIPELINE)
    if not pipe_path.exists():
        return []
    try:
        saved = joblib.load(pipe_path)
        prep = _prep_text(query)
        if isinstance(saved, dict):
            if saved.get("mode") == "single":
                vec = saved["vectorizer"].transform([prep]).toarray()
                q_vec = Normalizer().transform(vec)[0]
            else:
                q_vec = saved["pipeline"].transform([prep])[0]
        else:
            q_vec = saved.transform([prep])[0]
        return _search_npz(LOCAL_EMBEDDINGS_FILE, q_vec, top_k, min_score, "lsa")
    except Exception:
        return []


def _openai_semantic_search(query: str, top_k: int, min_score: float) -> List[Dict[str, Any]]:
    client = _openai_client()
    if not client or not data_path(OPENAI_EMBEDDINGS_FILE).exists():
        return []
    vecs = _openai_embed(client, [query])
    if not vecs or not vecs[0]:
        return []
    q_vec = np.array(vecs[0], dtype=np.float32)
    return _search_npz(OPENAI_EMBEDDINGS_FILE, q_vec, top_k, min_score, "openai")


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


def _rrf_merge(lists: List[List[Dict[str, Any]]], top_k: int, k: int = 60) -> List[Dict[str, Any]]:
    scores: Dict[str, float] = {}
    meta: Dict[str, Dict[str, Any]] = {}
    for lst in lists:
        for rank, item in enumerate(lst):
            cid = str(item.get("chunk_id") or "")
            if not cid:
                continue
            scores[cid] = scores.get(cid, 0.0) + 1.0 / (k + rank + 1)
            meta[cid] = item
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)[: max(1, int(top_k or 8))]
    out: List[Dict[str, Any]] = []
    for cid, rrf in ranked:
        row = dict(meta[cid])
        row["score"] = round(rrf, 4)
        row["method"] = "hybrid-vec"
        out.append(row)
    return out


def vector_search(query: str, top_k: int = 8, min_score: float = 0.04) -> List[Dict[str, Any]]:
    lists = [
        _local_semantic_search(query, top_k, max(0.12, min_score)),
        _openai_semantic_search(query, top_k, max(0.32, min_score)),
        _tfidf_search(query, top_k, min_score),
    ]
    lists = [lst for lst in lists if lst]
    if len(lists) > 1:
        return _rrf_merge(lists, top_k)
    return lists[0][:top_k] if lists else []


__all__ = ["rebuild_vector_index", "vector_search", "get_index_status", "LOCAL_EMBED_MODEL"]
