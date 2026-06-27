"""Hybrid local retrieval: keyword + TF-IDF vectors + legacy books."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from AI.engine.ai_knowledge_ingestor import _normalize_ar, _tokenize, get_sources_summary, load_all_chunks


def _score_chunk(query_tokens: List[str], chunk: Dict[str, Any]) -> float:
    if not query_tokens:
        return 0.0
    chunk_tokens = set(chunk.get("tokens") or _tokenize(chunk.get("text", "")))
    if not chunk_tokens:
        return 0.0
    qset = set(query_tokens)
    overlap = len(qset & chunk_tokens)
    if overlap == 0:
        text = _normalize_ar(chunk.get("text", ""))
        q = _normalize_ar(" ".join(query_tokens))
        if len(q) >= 4 and q in text:
            return 0.85
        return 0.0
    coverage = overlap / max(len(qset), 1)
    density = overlap / max(len(chunk_tokens), 1)
    title_boost = 0.1 if any(t in _normalize_ar(chunk.get("title", "")) for t in qset) else 0.0
    return min(1.0, coverage * 0.75 + density * 0.25 + title_boost)


def _keyword_retrieve(query: str, top_k: int, min_score: float) -> List[Dict[str, Any]]:
    query_tokens = _tokenize(query)
    if not query_tokens:
        return []
    scored: List[tuple] = []
    for chunk in load_all_chunks():
        score = _score_chunk(query_tokens, chunk)
        if score >= min_score:
            scored.append((score, chunk))
    scored.sort(key=lambda x: x[0], reverse=True)
    results: List[Dict[str, Any]] = []
    for score, chunk in scored[: max(1, int(top_k or 5))]:
        results.append(
            {
                "score": round(score, 3),
                "chunk_id": chunk.get("chunk_id"),
                "source_id": chunk.get("source_id"),
                "title": chunk.get("title"),
                "text": chunk.get("text"),
                "method": "keyword",
            }
        )
    return results


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
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)[: max(1, int(top_k or 5))]
    out: List[Dict[str, Any]] = []
    for cid, rrf in ranked:
        row = dict(meta[cid])
        row["score"] = round(rrf, 4)
        row["method"] = "hybrid"
        out.append(row)
    return out


def retrieve_chunks(query: str, top_k: int = 5, min_score: float = 0.08) -> List[Dict[str, Any]]:
    kw = _keyword_retrieve(query, top_k=top_k * 2, min_score=min_score)
    try:
        from AI.engine.ai_knowledge_vectors import vector_search
        vec = vector_search(query, top_k=top_k * 2, min_score=max(0.03, min_score * 0.5))
    except Exception:
        vec = []
    if kw and vec:
        return _rrf_merge([kw, vec], top_k=top_k)
    return kw or vec


def retrieve_knowledge_context(query: str, top_k: int = 5) -> Dict[str, Any]:
    chunks = retrieve_chunks(query, top_k=top_k)
    summary = get_sources_summary()
    return {
        "query": query,
        "chunks": chunks,
        "sources_available": summary.get("total_sources", 0),
        "chunks_indexed": summary.get("total_chunks", 0),
    }


def format_knowledge_context(chunks: List[Dict[str, Any]], max_chars: int = 6000) -> str:
    if not chunks:
        return ""
    parts = ["مصادر المعرفة المفهرسة:\n"]
    used = 0
    for i, chunk in enumerate(chunks, 1):
        title = chunk.get("title") or chunk.get("source_id") or f"مصدر {i}"
        text = str(chunk.get("text") or "").strip()
        block = f"\n[{i}] {title} (score={chunk.get('score', 0)}):\n{text}\n"
        if used + len(block) > max_chars:
            break
        parts.append(block)
        used += len(block)
    return "".join(parts)


def try_knowledge_answer(query: str, top_k: int = 4) -> Optional[str]:
    try:
        from AI.engine.ai_conversation import get_small_talk_response
        if get_small_talk_response(query):
            return None
    except Exception:
        pass

    chunks = retrieve_chunks(query, top_k=top_k, min_score=0.10)
    if not chunks:
        try:
            from AI.engine.ai_book_reader import get_book_reader
            legacy = get_book_reader().answer_from_books(query)
            if legacy:
                return legacy
        except Exception:
            pass
        return None

    lines = [f"📚 **من مصادر المعرفة المحلية** ({len(chunks)} مقطع — بحث هجين):\n"]
    for chunk in chunks:
        title = chunk.get("title") or "مصدر"
        snippet = str(chunk.get("text") or "").strip()
        if len(snippet) > 600:
            snippet = snippet[:600] + "…"
        lines.append(f"\n**{title}**\n{snippet}")
    lines.append("\n\n_مصدر: RAG هجين (LSA محلي + TF-IDF + OpenAI اختياري)._")
    return "\n".join(lines)


def build_llm_knowledge_addon(query: str) -> str:
    ctx = retrieve_knowledge_context(query, top_k=5)
    return format_knowledge_context(ctx.get("chunks") or [])


__all__ = [
    "retrieve_chunks",
    "retrieve_knowledge_context",
    "format_knowledge_context",
    "try_knowledge_answer",
    "build_llm_knowledge_addon",
]
