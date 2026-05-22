"""نطاق الشركة/الفرع للمستخدم والتقارير — قاعدة واحدة بدون tenants."""
from __future__ import annotations

from typing import List, Optional, Set

from flask_login import current_user


def get_accessible_branch_ids() -> Optional[List[int]]:
    """None = كل الفروع (مدير)، وإلا قائمة معرفات."""
    try:
        import utils
        if utils.is_super() or utils.is_admin():
            return None
    except Exception:
        pass
    try:
        u = current_user
        if not u or not getattr(u, "is_authenticated", False):
            return []
        links = getattr(u, "user_branches", None) or []
        ids = [int(ub.branch_id) for ub in links if getattr(ub, "branch_id", None)]
        return ids or []
    except Exception:
        return []


def get_accessible_company_ids() -> Optional[List[int]]:
    from extensions import db
    from models import Branch

    branch_ids = get_accessible_branch_ids()
    if branch_ids is None:
        return None
    if not branch_ids:
        return []
    rows = (
        db.session.query(Branch.company_id)
        .filter(Branch.id.in_(branch_ids), Branch.company_id.isnot(None))
        .distinct()
        .all()
    )
    return list({int(r[0]) for r in rows if r[0]})


def filter_by_branches(query, branch_column):
    ids = get_accessible_branch_ids()
    if ids is None:
        return query
    if not ids:
        return query.filter(branch_column == -1)
    return query.filter(branch_column.in_(ids))


def default_company():
    from models import Company
    return Company.query.filter_by(is_active=True).order_by(Company.id.asc()).first()
