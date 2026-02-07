"""add_composite_indexes_for_settlements

Revision ID: b1a3f0c6d8a9
Revises: 79cf2ae42e8e
Create Date: 2026-01-31 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "b1a3f0c6d8a9"
down_revision = "79cf2ae42e8e"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("exchange_transactions", schema=None) as batch_op:
        batch_op.create_index(
            "ix_exchange_supplier_dir_created_at",
            ["supplier_id", "direction", "created_at"],
            unique=False,
        )
        batch_op.create_index(
            "ix_exchange_partner_dir_created_at",
            ["partner_id", "direction", "created_at"],
            unique=False,
        )

    with op.batch_alter_table("payments", schema=None) as batch_op:
        batch_op.create_index(
            "ix_pay_supplier_dir_status_date",
            ["supplier_id", "direction", "status", "payment_date"],
            unique=False,
        )
        batch_op.create_index(
            "ix_pay_partner_dir_status_date",
            ["partner_id", "direction", "status", "payment_date"],
            unique=False,
        )
        batch_op.create_index(
            "ix_pay_customer_dir_status_date",
            ["customer_id", "direction", "status", "payment_date"],
            unique=False,
        )

    with op.batch_alter_table("expenses", schema=None) as batch_op:
        batch_op.create_index(
            "ix_expense_payee_type_entity_date",
            ["payee_type", "payee_entity_id", "date"],
            unique=False,
        )


def downgrade():
    with op.batch_alter_table("expenses", schema=None) as batch_op:
        batch_op.drop_index("ix_expense_payee_type_entity_date")

    with op.batch_alter_table("payments", schema=None) as batch_op:
        batch_op.drop_index("ix_pay_customer_dir_status_date")
        batch_op.drop_index("ix_pay_partner_dir_status_date")
        batch_op.drop_index("ix_pay_supplier_dir_status_date")

    with op.batch_alter_table("exchange_transactions", schema=None) as batch_op:
        batch_op.drop_index("ix_exchange_partner_dir_created_at")
        batch_op.drop_index("ix_exchange_supplier_dir_created_at")
