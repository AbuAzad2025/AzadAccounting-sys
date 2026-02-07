from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Any

from extensions import db
from services.accounting_demo_seed import seed_accounting_demo


def seed_owner_security_demo(*, tag: str | None = None, days_ago: int = 0, scale: int = 2) -> dict[str, Any]:
    payload = seed_accounting_demo(
        tag=tag,
        days_ago=days_ago,
        with_settlements=True,
        update_balances=False,
        cover_all_gl_types=True,
        full_system=True,
        scale=scale,
    )

    import models as m

    seed_tag = (tag or "").strip() or "OWNSEC"
    now = datetime.now(timezone.utc)

    sys_username = f"__SYS_{seed_tag}__"
    with db.session.no_autoflush:
        sys_user = db.session.query(m.User).filter(m.User.username == sys_username).first()
        role_id = db.session.query(m.Role.id).order_by(m.Role.id.asc()).scalar()
        plan = db.session.query(m.SaaSPlan).order_by(m.SaaSPlan.id.asc()).first()
        customer = db.session.query(m.Customer).order_by(m.Customer.id.asc()).first()
        sub = db.session.query(m.SaaSSubscription).order_by(m.SaaSSubscription.id.asc()).first()
        inv = db.session.query(m.SaaSInvoice).order_by(m.SaaSInvoice.id.asc()).first()
    if not sys_user:
        sys_user = m.User(
            username=sys_username,
            email=f"{seed_tag.lower()}@example.com",
            role_id=role_id,
            is_active=True,
            is_system_account=True,
        )
        sys_user.set_password("test-pass")
        db.session.add(sys_user)
        db.session.flush()

    if not plan:
        plan = m.SaaSPlan(
            name=f"Plan {seed_tag}",
            description="Seeded plan",
            price_monthly=Decimal("10.00"),
            price_yearly=Decimal("100.00"),
            currency="USD",
            max_users=5,
            max_invoices=100,
            storage_gb=5,
            features="seed",
            is_popular=True,
            sort_order=10,
        )
        db.session.add(plan)
        db.session.flush()

    if not customer:
        customer = m.Customer(name=f"Customer {seed_tag}", phone="0500000000")
        db.session.add(customer)
        db.session.flush()

    if not sub:
        start_date = now - timedelta(days=days_ago)
        sub = m.SaaSSubscription(
            customer_id=customer.id,
            plan_id=plan.id,
            status="active",
            start_date=start_date,
            end_date=start_date + timedelta(days=30),
        )
        db.session.add(sub)
        db.session.flush()

    if not inv:
        invoice_no = f"INV-{seed_tag}-{int(now.timestamp())}"
        inv = m.SaaSInvoice(
            invoice_number=invoice_no,
            subscription_id=sub.id,
            amount=Decimal("10.00"),
            currency="USD",
            status="pending",
            due_date=now + timedelta(days=7),
        )
        db.session.add(inv)
        db.session.flush()

    has_auth = db.session.query(m.AuthAudit.id).limit(1).scalar() is not None
    if not has_auth:
        db.session.add(
            m.AuthAudit(
                user_id=payload.get("owner_user_id"),
                event="LOGIN",
                success=True,
                ip="127.0.0.1",
                user_agent="pytest",
                note="seed",
                meta={"seed": seed_tag},
            )
        )

    db.session.add(
        m.AuditLog(
            model_name="SystemSettings",
            record_id=None,
            user_id=payload.get("owner_user_id"),
            customer_id=None,
            action="VIEW",
            old_data=None,
            new_data=None,
            ip_address="127.0.0.1",
            user_agent="pytest",
        )
    )

    db.session.commit()

    payload.update(
        {
            "seed_tag": seed_tag,
            "system_username": sys_username,
            "system_password": "test-pass",
            "first_customer_id": int(customer.id) if customer else None,
            "saas_plan_id": int(plan.id),
            "saas_subscription_id": int(sub.id),
            "saas_invoice_id": int(inv.id),
        }
    )
    return payload
