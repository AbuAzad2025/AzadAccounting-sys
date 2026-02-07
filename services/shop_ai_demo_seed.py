from __future__ import annotations

from decimal import Decimal
from typing import Any

from extensions import db
from services.accounting_demo_seed import seed_accounting_demo


def seed_shop_ai_demo(
    *,
    tag: str | None = None,
    days_ago: int = 0,
    scale: int = 2,
) -> dict[str, Any]:
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

    seed_tag = (tag or "").strip() or "SHOPAI"

    cat_name = f"متجر {seed_tag}"
    with db.session.no_autoflush:
        cat = db.session.query(m.ProductCategory).filter(m.ProductCategory.name == cat_name).first()
    if not cat:
        cat = m.ProductCategory(name=cat_name, description=f"تصنيف تجريبي {seed_tag}")
        db.session.add(cat)
        db.session.flush()

    online_val = getattr(m.WarehouseType, "ONLINE").value if hasattr(m.WarehouseType, "ONLINE") else "ONLINE"
    with db.session.no_autoflush:
        q_wh = db.session.query(m.Warehouse).filter(m.Warehouse.is_active.is_(True))
        if hasattr(m.Warehouse, "online_is_default"):
            q_wh = q_wh.filter(m.Warehouse.online_is_default.is_(True))
        wh_online = q_wh.first()
        if not wh_online:
            wh_online = (
                db.session.query(m.Warehouse)
                .filter(m.Warehouse.is_active.is_(True))
                .filter(m.Warehouse.warehouse_type == online_val)
                .first()
            )
        if not wh_online:
            wh_online = db.session.query(m.Warehouse).filter(m.Warehouse.is_active.is_(True)).first()

    if wh_online and hasattr(wh_online, "online_is_default"):
        wh_online.online_is_default = True

    with db.session.no_autoflush:
        products = db.session.query(m.Product).order_by(m.Product.id.asc()).limit(4).all()
    if len(products) < 4:
        for i in range(4 - len(products)):
            p = m.Product(
                name=f"منتج متجر {seed_tag} {i+1}",
                currency="ILS",
                price=Decimal("100.00"),
                selling_price=Decimal("100.00"),
                purchase_price=Decimal("60.00"),
                tax_rate=Decimal("0.00"),
                is_active=True,
                is_published=True,
            )
            db.session.add(p)
        db.session.flush()
        products = db.session.query(m.Product).order_by(m.Product.id.asc()).limit(4).all()

    for idx, p in enumerate(products):
        p.is_active = True
        if hasattr(p, "is_published"):
            p.is_published = True
        if hasattr(p, "category_id"):
            p.category_id = cat.id
        if hasattr(p, "online_name"):
            p.online_name = (p.online_name or f"{p.name} (أونلاين)").strip()
        if hasattr(p, "online_price"):
            base_price = p.online_price if getattr(p, "online_price", None) not in (None, 0) else (p.selling_price or p.price or 0)
            try:
                base_price = Decimal(str(base_price))
            except Exception:
                base_price = Decimal("0")
            p.online_price = (base_price if base_price > 0 else Decimal("100.00")) + Decimal(str(idx))

        if wh_online:
            sl = (
                db.session.query(m.StockLevel)
                .filter(m.StockLevel.product_id == p.id, m.StockLevel.warehouse_id == wh_online.id)
                .first()
            )
            if not sl:
                kwargs = {"product_id": p.id, "warehouse_id": wh_online.id, "quantity": 0}
                if hasattr(m.StockLevel, "reserved_quantity"):
                    kwargs["reserved_quantity"] = 0
                sl = m.StockLevel(**kwargs)
                db.session.add(sl)
                db.session.flush()
            sl.quantity = max(int(sl.quantity or 0), 50)
            if hasattr(sl, "reserved_quantity"):
                sl.reserved_quantity = 0

    extra = m.Product(
        name=f"منتج توصيات {seed_tag}",
        currency="ILS",
        price=Decimal("150.00"),
        selling_price=Decimal("150.00"),
        purchase_price=Decimal("90.00"),
        tax_rate=Decimal("0.00"),
        is_active=True,
        is_published=True,
        category_id=cat.id,
        online_name=f"منتج توصيات {seed_tag} (أونلاين)",
        online_price=Decimal("155.00"),
    )
    db.session.add(extra)
    db.session.flush()
    if wh_online:
        kwargs = {"product_id": extra.id, "warehouse_id": wh_online.id, "quantity": 80}
        if hasattr(m.StockLevel, "reserved_quantity"):
            kwargs["reserved_quantity"] = 0
        db.session.add(m.StockLevel(**kwargs))

    db.session.commit()

    payload.update(
        {
            "shop_category_id": int(cat.id),
            "shop_online_warehouse_id": int(wh_online.id) if wh_online else None,
            "shop_product_ids": [int(p.id) for p in products] + [int(extra.id)],
        }
    )
    return payload
