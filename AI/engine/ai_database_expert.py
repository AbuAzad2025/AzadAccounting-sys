"""AI Database Expert.

Static SQL/schema analyzer. It does not execute user SQL and does not claim fake
performance percentages.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

from sqlalchemy import inspect

from extensions import db


class DatabaseExpert:
    def __init__(self):
        self.common_patterns = self._load_common_patterns()

    def analyze_query(self, query: str) -> Dict[str, Any]:
        query = str(query or "")
        analysis = {
            "query": query,
            "issues": [],
            "performance_score": 100,
            "suggestions": [],
            "optimized_query": None,
            "estimated_complexity": "unknown",
        }
        upper = query.upper()

        if "SELECT *" in upper:
            analysis["issues"].append({"type": "bad_practice", "severity": "medium", "message": "استخدام SELECT * - حدد الأعمدة المطلوبة فقط", "fix": "استبدل * بأسماء الأعمدة المحددة"})
            analysis["performance_score"] -= 10

        if "WHERE" not in upper and "SELECT" in upper:
            analysis["issues"].append({"type": "missing_where", "severity": "high", "message": "لا يوجد WHERE clause - قد يعيد جميع السجلات", "fix": "أضف WHERE لتحديد السجلات المطلوبة"})
            analysis["performance_score"] -= 20
            analysis["estimated_complexity"] = "likely full table scan"

        if "LIMIT" not in upper and "SELECT" in upper:
            analysis["suggestions"].append("أضف LIMIT للحد من عدد النتائج المعادة عند الاستعراض")

        join_count = upper.count("JOIN")
        if join_count > 3:
            analysis["issues"].append({"type": "many_joins", "severity": "medium", "message": f"عدد كبير من JOINs ({join_count}) - قد يؤثر على الأداء", "fix": "راجع خطة التنفيذ أو فكر في indexes مناسبة"})
            analysis["performance_score"] -= (join_count - 3) * 5

        if re.search(r"LIKE\s+['\"]%.*%['\"]", query, re.IGNORECASE):
            analysis["issues"].append({"type": "slow_like", "severity": "high", "message": "LIKE %...% بطيء غالباً ولا يستفيد من index عادي", "fix": "استخدم Full-Text Search أو نمط يبدأ بحرف ثابت إذا أمكن"})
            analysis["performance_score"] -= 25

        or_count = len(re.findall(r"\bOR\b", query, re.IGNORECASE))
        if or_count > 2:
            analysis["suggestions"].append(f"عدد كبير من OR ({or_count}) - فكر في استخدام IN إذا كانت المقارنة على نفس العمود")

        if "SELECT" in query[10:].upper():
            analysis["suggestions"].append("يوجد subquery - راجع إن كان JOIN أو EXISTS أفضل حسب خطة التنفيذ")

        analysis["performance_score"] = max(0, min(100, analysis["performance_score"]))
        return analysis

    def suggest_index(self, table_name: str, query_pattern: str) -> List[Dict]:
        table_name = str(table_name or "").strip()
        query_pattern = str(query_pattern or "")
        suggestions = []
        if not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", table_name):
            return suggestions

        where_match = re.search(r"WHERE\s+(\w+)", query_pattern, re.IGNORECASE)
        if where_match:
            column = where_match.group(1)
            suggestions.append({"type": "single_column_index", "table": table_name, "columns": [column], "sql": f"CREATE INDEX idx_{table_name}_{column} ON {table_name}({column});", "reason": f"لتسريع WHERE {column}"})

        join_matches = re.findall(r"JOIN\s+\w+\s+ON\s+\w+\.(\w+)", query_pattern, re.IGNORECASE)
        for column in join_matches:
            suggestions.append({"type": "foreign_key_index", "table": table_name, "columns": [column], "sql": f"CREATE INDEX idx_{table_name}_{column}_fk ON {table_name}({column});", "reason": f"لتسريع JOIN على {column}"})
        return suggestions

    def detect_n_plus_one(self, code_context: str) -> Optional[Dict]:
        pattern = r"for\s+\w+\s+in\s+.*:\s*\n.*\.query\."
        if re.search(pattern, str(code_context or ""), re.MULTILINE):
            return {
                "detected": True,
                "issue": "N+1 Query Problem",
                "explanation": "يتم تنفيذ query منفصل لكل عنصر داخل loop. استخدم eager loading مثل joinedload أو subqueryload عند الحاجة.",
                "solution": "استخدم eager loading: joinedload() أو subqueryload()",
            }
        return None

    def analyze_schema(self, table_name: str) -> Dict[str, Any]:
        try:
            table_name = str(table_name or "").strip()
            inspector = inspect(db.engine)
            if table_name not in inspector.get_table_names():
                return {"error": f"Table not found: {table_name}"}

            columns = inspector.get_columns(table_name)
            fks = inspector.get_foreign_keys(table_name)
            indexes = inspector.get_indexes(table_name)
            analysis = {"table_name": table_name, "total_columns": len(columns), "total_fks": len(fks), "total_indexes": len(indexes), "issues": [], "recommendations": []}

            pk = inspector.get_pk_constraint(table_name)
            if not pk.get("constrained_columns"):
                analysis["issues"].append({"type": "no_primary_key", "severity": "critical", "message": "الجدول لا يحتوي على Primary Key"})

            fk_columns = {col for fk in fks for col in fk.get("constrained_columns", [])}
            indexed_columns = {col for idx in indexes for col in idx.get("column_names", [])}
            unindexed_fks = fk_columns - indexed_columns
            if unindexed_fks:
                analysis["recommendations"].append({"type": "add_fk_indexes", "message": f"أضف indexes على FK: {', '.join(sorted(unindexed_fks))}"})

            if len(columns) > 30:
                analysis["recommendations"].append({"type": "review_table_width", "message": f"الجدول يحتوي على {len(columns)} عمود - راجع إن كان التقسيم مناسباً"})

            nullable_count = sum(1 for col in columns if col.get("nullable", True))
            if columns and nullable_count > len(columns) * 0.7:
                analysis["recommendations"].append({"type": "review_nullables", "message": f"{nullable_count} عمود nullable - راجع القيم الافتراضية والتحقق"})
            return analysis
        except Exception as exc:
            return {"error": str(exc)}

    def suggest_query_optimization(self, slow_query: str) -> Dict[str, Any]:
        slow_query = str(slow_query or "")
        optimizations = []
        upper = slow_query.upper()

        if "SELECT *" in upper:
            optimizations.append({"type": "specific_columns", "before": "SELECT *", "after": "SELECT column1, column2, ...", "benefit": "تقليل البيانات المنقولة"})
        if "LIMIT" not in upper and "SELECT" in upper:
            optimizations.append({"type": "add_limit", "before": slow_query, "after": slow_query + " LIMIT 100", "benefit": "تحديد عدد النتائج عند الاستعراض"})
        if "COUNT(*)" in upper and "WHERE" in upper:
            optimizations.append({"type": "use_exists", "before": "SELECT COUNT(*) FROM table WHERE condition", "after": "SELECT EXISTS(SELECT 1 FROM table WHERE condition LIMIT 1)", "benefit": "EXISTS قد يكون أسرع للتحقق من الوجود"})
        if len(re.findall(r"\bOR\b", slow_query, re.IGNORECASE)) > 2:
            optimizations.append({"type": "use_in", "before": "WHERE col = 1 OR col = 2 OR col = 3", "after": "WHERE col IN (1, 2, 3)", "benefit": "IN أوضح وقد يساعد المحسن حسب الحالة"})

        return {"original_query": slow_query, "optimizations": optimizations, "estimated_improvement": "requires EXPLAIN/ANALYZE"}

    def _load_common_patterns(self) -> Dict:
        return {
            "slow_patterns": [r"SELECT \* FROM", r"LIKE [\"']%.*%[\"']", r"OR.*OR.*OR"],
            "good_patterns": [r"SELECT \w+, \w+ FROM", r"WHERE.*LIMIT", r".*INDEX"],
        }


_db_expert = None


def get_database_expert() -> DatabaseExpert:
    global _db_expert
    if _db_expert is None:
        _db_expert = DatabaseExpert()
    return _db_expert


__all__ = ["DatabaseExpert", "get_database_expert"]
