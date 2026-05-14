"""AI Learning System.

Stores compact learned responses, error corrections, and reusable response
patterns. Uses ai_storage for consistent runtime JSON handling.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from typing import Dict, Optional

from AI.engine.ai_storage import read_json, sync_training_manifest, write_json

LEARNED_RESPONSES_FILE = "learned_responses.json"
MAX_RESPONSES_PER_QUERY = 10
MAX_PATTERNS_PER_TYPE = 100


class LearningSystem:
    def __init__(self):
        self.learned_responses = {}
        self.error_corrections = {}
        self.pattern_library = defaultdict(list)
        self.performance_data = []
        self._load_learned_data()

    def _load_learned_data(self):
        data = read_json(LEARNED_RESPONSES_FILE, {})
        if not isinstance(data, dict):
            return
        self.learned_responses = data.get("responses", {}) if isinstance(data.get("responses", {}), dict) else {}
        self.error_corrections = data.get("corrections", {}) if isinstance(data.get("corrections", {}), dict) else {}
        self.pattern_library = defaultdict(list, data.get("patterns", {}) if isinstance(data.get("patterns", {}), dict) else {})

    def learn_from_interaction(self, query: str, response: str, feedback: str = None):
        query_normalized = self._normalize_query(query)
        if not query_normalized:
            return

        learned = self.learned_responses.setdefault(
            query_normalized,
            {"responses": [], "best_response": None, "count": 0, "success_count": 0},
        )

        learned["responses"].append({"response": response, "timestamp": datetime.now().isoformat(), "feedback": feedback})
        learned["responses"] = learned["responses"][-MAX_RESPONSES_PER_QUERY:]
        learned["count"] += 1

        if feedback == "positive" or feedback is None:
            learned["success_count"] += 1
            learned["best_response"] = response

        self._extract_patterns(query, response)
        self._save_learned_data()

    def learn_error_correction(self, error_type: str, solution: str):
        error_type = self._normalize_query(error_type)
        if not error_type or not solution:
            return
        corrections = self.error_corrections.setdefault(error_type, [])
        corrections.append({"solution": solution, "timestamp": datetime.now().isoformat(), "use_count": 0})
        self.error_corrections[error_type] = corrections[-MAX_RESPONSES_PER_QUERY:]
        self._save_learned_data()

    def get_learned_response(self, query: str) -> Optional[str]:
        query_normalized = self._normalize_query(query)
        if query_normalized in self.learned_responses:
            learned = self.learned_responses[query_normalized]
            if learned.get("best_response"):
                learned["count"] += 1
                self._save_learned_data()
                return learned["best_response"]
        return self._find_similar_learned(query_normalized)

    def _normalize_query(self, query: str) -> str:
        return " ".join(str(query or "").lower().strip().split())

    def _extract_patterns(self, query: str, response: str):
        q_lower = str(query or "").lower()
        response_lower = str(response or "").lower()
        if "كيف" in q_lower and "خطوات" in response_lower:
            self._add_pattern("how_to_questions", {"query_pattern": "كيف + [action]", "response_pattern": "step_by_step", "example": str(query)[:100]})
        if "رصيد" in q_lower and "₪" in str(response):
            self._add_pattern("balance_queries", {"query_pattern": "رصيد + [entity]", "response_pattern": "balance_with_currency", "example": str(query)[:100]})

    def _add_pattern(self, pattern_type: str, item: Dict):
        patterns = self.pattern_library[pattern_type]
        if item not in patterns:
            patterns.append(item)
        self.pattern_library[pattern_type] = patterns[-MAX_PATTERNS_PER_TYPE:]

    def _find_similar_learned(self, query_normalized: str) -> Optional[str]:
        best_response = None
        best_similarity = 0.0
        for learned_q, data in self.learned_responses.items():
            similarity = self._calculate_similarity(query_normalized, learned_q)
            if similarity > best_similarity and similarity > 0.8:
                best_similarity = similarity
                best_response = data.get("best_response")
        return best_response

    def _calculate_similarity(self, q1: str, q2: str) -> float:
        words1 = set(q1.split())
        words2 = set(q2.split())
        if not words1 or not words2:
            return 0.0
        return len(words1 & words2) / len(words1 | words2)

    def _save_learned_data(self):
        try:
            write_json(
                LEARNED_RESPONSES_FILE,
                {
                    "responses": self.learned_responses,
                    "corrections": self.error_corrections,
                    "patterns": dict(self.pattern_library),
                    "last_updated": datetime.now().isoformat(),
                },
            )
            sync_training_manifest(extra_files=[LEARNED_RESPONSES_FILE])
        except Exception as exc:
            print(f"Error saving learned data: {exc}")

    def get_learning_stats(self) -> Dict:
        return {
            "total_learned_queries": len(self.learned_responses),
            "total_corrections": sum(len(corr) for corr in self.error_corrections.values()),
            "total_patterns": sum(len(patterns) for patterns in self.pattern_library.values()),
            "success_rate": self._calculate_success_rate(),
        }

    def _calculate_success_rate(self) -> float:
        if not self.learned_responses:
            return 0.0
        total_success = sum(int(data.get("success_count", 0) or 0) for data in self.learned_responses.values())
        total_count = sum(int(data.get("count", 0) or 0) for data in self.learned_responses.values())
        return (total_success / total_count) * 100 if total_count else 0.0


_learning_system = None


def get_learning_system():
    global _learning_system
    if _learning_system is None:
        _learning_system = LearningSystem()
    return _learning_system


__all__ = ["LearningSystem", "get_learning_system"]
