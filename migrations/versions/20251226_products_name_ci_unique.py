"""merge duplicate products by name and enforce case-insensitive uniqueness

Revision ID: 20251226_products_name_ci_unique
Revises: c0f7a1b2c3d4
Create Date: 2025-12-26 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text as sa_text


revision = "20251226_products_name_ci_unique"
down_revision = "c0f7a1b2c3d4"
branch_labels = None
depends_on = None


def _has_table(bind, name: str) -> bool:
    insp = sa.inspect(bind)
    try:
        return insp.has_table(name)
    except Exception:
        try:
            return name in set(insp.get_table_names())
        except Exception:
            return False


def _merge_stock_levels(bind, winner_id: int, loser_id: int) -> None:
    if not _has_table(bind, "stock_levels"):
        return
    bind.execute(
        sa_text(
            """
            INSERT INTO stock_levels (product_id, warehouse_id, quantity, reserved_quantity, min_stock, max_stock)
            SELECT :winner, warehouse_id, quantity, reserved_quantity, min_stock, max_stock
            FROM stock_levels
            WHERE product_id = :loser
            ON CONFLICT (product_id, warehouse_id) DO UPDATE SET
                quantity = stock_levels.quantity + EXCLUDED.quantity,
                reserved_quantity = stock_levels.reserved_quantity + EXCLUDED.reserved_quantity,
                min_stock = COALESCE(stock_levels.min_stock, EXCLUDED.min_stock),
                max_stock = COALESCE(stock_levels.max_stock, EXCLUDED.max_stock)
            """
        ),
        {"winner": winner_id, "loser": loser_id},
    )
    bind.execute(sa_text("DELETE FROM stock_levels WHERE product_id = :loser"), {"loser": loser_id})


def _merge_warehouse_partner_shares(bind, winner_id: int, loser_id: int) -> None:
    if not _has_table(bind, "warehouse_partner_shares"):
        return
    bind.execute(
        sa_text(
            """
            INSERT INTO warehouse_partner_shares (partner_id, warehouse_id, product_id, share_percentage, share_amount, notes)
            SELECT partner_id, warehouse_id, :winner, share_percentage, share_amount, notes
            FROM warehouse_partner_shares
            WHERE product_id = :loser
            ON CONFLICT (partner_id, warehouse_id, product_id) DO UPDATE SET
                share_percentage = GREATEST(warehouse_partner_shares.share_percentage, EXCLUDED.share_percentage),
                share_amount = COALESCE(warehouse_partner_shares.share_amount, EXCLUDED.share_amount),
                notes = COALESCE(warehouse_partner_shares.notes, EXCLUDED.notes)
            """
        ),
        {"winner": winner_id, "loser": loser_id},
    )
    bind.execute(sa_text("DELETE FROM warehouse_partner_shares WHERE product_id = :loser"), {"loser": loser_id})


def _merge_shipment_items(bind, winner_id: int, loser_id: int) -> None:
    if not _has_table(bind, "shipment_items"):
        return
    bind.execute(
        sa_text(
            """
            INSERT INTO shipment_items (
                shipment_id, product_id, warehouse_id, quantity, unit_cost, declared_value, landed_extra_share, landed_unit_cost, notes
            )
            SELECT
                shipment_id, :winner, warehouse_id, quantity, unit_cost, declared_value, landed_extra_share, landed_unit_cost, notes
            FROM shipment_items
            WHERE product_id = :loser
            ON CONFLICT (shipment_id, product_id, warehouse_id) DO UPDATE SET
                quantity = shipment_items.quantity + EXCLUDED.quantity,
                unit_cost = GREATEST(shipment_items.unit_cost, EXCLUDED.unit_cost),
                declared_value = COALESCE(shipment_items.declared_value, EXCLUDED.declared_value),
                landed_extra_share = COALESCE(shipment_items.landed_extra_share, 0) + COALESCE(EXCLUDED.landed_extra_share, 0),
                landed_unit_cost = (
                    GREATEST(shipment_items.unit_cost, EXCLUDED.unit_cost)
                    + (COALESCE(shipment_items.landed_extra_share, 0) + COALESCE(EXCLUDED.landed_extra_share, 0))
                      / NULLIF((shipment_items.quantity + EXCLUDED.quantity), 0)
                ),
                notes = COALESCE(shipment_items.notes, EXCLUDED.notes)
            """
        ),
        {"winner": winner_id, "loser": loser_id},
    )
    bind.execute(sa_text("DELETE FROM shipment_items WHERE product_id = :loser"), {"loser": loser_id})


def _merge_online_cart_items(bind, winner_id: int, loser_id: int) -> None:
    if not _has_table(bind, "online_cart_items"):
        return
    bind.execute(
        sa_text(
            """
            INSERT INTO online_cart_items (cart_id, product_id, quantity, price, added_at)
            SELECT cart_id, :winner, quantity, price, added_at
            FROM online_cart_items
            WHERE product_id = :loser
            ON CONFLICT (cart_id, product_id) DO UPDATE SET
                quantity = online_cart_items.quantity + EXCLUDED.quantity,
                price = CASE
                    WHEN online_cart_items.price IS NULL OR online_cart_items.price = 0 THEN EXCLUDED.price
                    ELSE online_cart_items.price
                END,
                added_at = LEAST(online_cart_items.added_at, EXCLUDED.added_at)
            """
        ),
        {"winner": winner_id, "loser": loser_id},
    )
    bind.execute(sa_text("DELETE FROM online_cart_items WHERE product_id = :loser"), {"loser": loser_id})


def _merge_online_preorder_items(bind, winner_id: int, loser_id: int) -> None:
    if not _has_table(bind, "online_preorder_items"):
        return
    bind.execute(
        sa_text(
            """
            INSERT INTO online_preorder_items (order_id, product_id, quantity, price)
            SELECT order_id, :winner, quantity, price
            FROM online_preorder_items
            WHERE product_id = :loser
            ON CONFLICT (order_id, product_id) DO UPDATE SET
                quantity = online_preorder_items.quantity + EXCLUDED.quantity,
                price = CASE
                    WHEN online_preorder_items.price IS NULL OR online_preorder_items.price = 0 THEN EXCLUDED.price
                    ELSE online_preorder_items.price
                END
            """
        ),
        {"winner": winner_id, "loser": loser_id},
    )
    bind.execute(sa_text("DELETE FROM online_preorder_items WHERE product_id = :loser"), {"loser": loser_id})


def _ensure_products_name_ci_unique_index(bind) -> None:
    if not str(getattr(bind.dialect, "name", "")).startswith("postgre"):
        return
    exists = bind.execute(
        sa_text(
            "SELECT 1 FROM pg_class WHERE relkind = 'i' AND relname = :name LIMIT 1"
        ),
        {"name": "uq_products_name_ci"},
    ).first()
    if not exists:
        bind.execute(sa_text("CREATE UNIQUE INDEX uq_products_name_ci ON products (lower(name))"))


def upgrade():
    bind = op.get_bind()
    if not str(getattr(bind.dialect, "name", "")).startswith("postgre"):
        return

    bind.execute(sa_text("UPDATE products SET name = btrim(name) WHERE name IS NOT NULL"))

    dup_rows = bind.execute(
        sa_text(
            """
            SELECT lower(btrim(name)) AS k, array_agg(id ORDER BY id) AS ids
            FROM products
            WHERE name IS NOT NULL AND btrim(name) <> ''
            GROUP BY lower(btrim(name))
            HAVING COUNT(*) > 1
            """
        )
    ).fetchall()

    fk_rows = bind.execute(
        sa_text(
            """
            SELECT
              conrelid::regclass::text AS table_name,
              a.attname AS column_name
            FROM pg_constraint c
            JOIN pg_attribute a ON a.attrelid = c.conrelid AND a.attnum = ANY(c.conkey)
            WHERE c.contype = 'f'
              AND c.confrelid = 'products'::regclass
            """
        )
    ).fetchall()

    prep = bind.dialect.identifier_preparer

    def _q_table(full_name: str) -> str:
        if "." in full_name:
            schema, tname = full_name.split(".", 1)
            return f"{prep.quote_schema(schema)}.{prep.quote(tname)}"
        return prep.quote(full_name)

    def _q_col(col: str) -> str:
        return prep.quote(col)

    for row in dup_rows:
        ids = list(row._mapping["ids"] or [])
        if len(ids) < 2:
            continue
        winner = int(ids[0])
        losers = [int(x) for x in ids[1:]]
        for loser in losers:
            _merge_stock_levels(bind, winner, loser)
            _merge_warehouse_partner_shares(bind, winner, loser)
            _merge_shipment_items(bind, winner, loser)
            _merge_online_cart_items(bind, winner, loser)
            _merge_online_preorder_items(bind, winner, loser)

            for fk in fk_rows:
                tname = fk._mapping["table_name"]
                cname = fk._mapping["column_name"]
                bind.execute(
                    sa_text(
                        f"UPDATE {_q_table(tname)} SET {_q_col(cname)} = :winner WHERE {_q_col(cname)} = :loser"
                    ),
                    {"winner": winner, "loser": loser},
                )

            bind.execute(sa_text("DELETE FROM products WHERE id = :loser"), {"loser": loser})

    _ensure_products_name_ci_unique_index(bind)


def downgrade():
    bind = op.get_bind()
    if not str(getattr(bind.dialect, "name", "")).startswith("postgre"):
        return
    bind.execute(sa_text("DROP INDEX IF EXISTS uq_products_name_ci"))
