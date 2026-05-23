"""ربط المستخدمين بالفروع."""
from __future__ import annotations

from typing import Iterable, List, Optional

from extensions import db
from models import UserBranch


def get_branch_ids_for_user(user_id: int) -> List[int]:
    rows = UserBranch.query.filter_by(user_id=int(user_id)).all()
    return [int(r.branch_id) for r in rows if r.branch_id]


def get_primary_branch_id(user_id: int) -> Optional[int]:
    row = (
        UserBranch.query.filter_by(user_id=int(user_id), is_primary=True)
        .order_by(UserBranch.id.asc())
        .first()
    )
    if row:
        return int(row.branch_id)
    ids = get_branch_ids_for_user(user_id)
    return ids[0] if ids else None


def sync_user_branches(
    user_id: int,
    branch_ids: Iterable[int],
    *,
    primary_branch_id: Optional[int] = None,
) -> None:
    wanted = sorted({int(b) for b in branch_ids if b})
    if not wanted:
        UserBranch.query.filter_by(user_id=int(user_id)).delete(synchronize_session=False)
        return

    primary = int(primary_branch_id) if primary_branch_id in wanted else wanted[0]
    existing = {
        int(r.branch_id): r
        for r in UserBranch.query.filter_by(user_id=int(user_id)).all()
    }

    for bid in wanted:
        if bid in existing:
            existing[bid].is_primary = bid == primary
            existing[bid].can_manage = bool(existing[bid].can_manage)
        else:
            db.session.add(
                UserBranch(
                    user_id=int(user_id),
                    branch_id=bid,
                    is_primary=bid == primary,
                    can_manage=False,
                )
            )

    for bid, row in existing.items():
        if bid not in wanted:
            db.session.delete(row)
