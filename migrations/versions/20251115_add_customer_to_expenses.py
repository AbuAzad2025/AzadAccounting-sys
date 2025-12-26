"""add customer link to expenses

Revision ID: 20251115_add_customer_to_expenses
Revises: 20251112_payment_deliverer_name
Create Date: 2025-11-15 22:30:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision = "20251115_add_customer_to_expenses"
down_revision = "20251112_payment_deliverer_name"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = inspect(bind)
    columns = {col["name"] for col in inspector.get_columns("expenses")}

    if "customer_id" not in columns:
        op.add_column(
            "expenses",
            sa.Column("customer_id", sa.Integer(), nullable=True),
        )
        op.create_index(
            "ix_expense_customer_id",
            "expenses",
            ["customer_id"],
        )
        op.create_foreign_key(
            op.f("fk_expenses_customer_id_customers"),
            "expenses",
            "customers",
            ["customer_id"],
            ["id"],
            ondelete="SET NULL",
        )

    indexes = {idx["name"] for idx in inspector.get_indexes("expenses")}
    if "ix_expense_customer_date" not in indexes:
        op.create_index(
            "ix_expense_customer_date",
            "expenses",
            ["customer_id", "date"],
        )


def downgrade():
    bind = op.get_bind()
    inspector = inspect(bind)
    indexes = {idx["name"] for idx in inspector.get_indexes("expenses")}

    if "ix_expense_customer_date" in indexes:
        op.drop_index("ix_expense_customer_date", table_name="expenses")
    if "ix_expense_customer_id" in indexes:
        op.drop_index("ix_expense_customer_id", table_name="expenses")

    fks = inspector.get_foreign_keys("expenses")
    fk_names = {fk["name"] for fk in fks}
    fk_name = op.f("fk_expenses_customer_id_customers")
    if fk_name in fk_names:
        op.drop_constraint(fk_name, "expenses", type_="foreignkey")

    columns = {col["name"] for col in inspector.get_columns("expenses")}
    if "customer_id" in columns:
        op.drop_column("expenses", "customer_id")

