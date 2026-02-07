"""expand_expense_payee_type_constraint

Revision ID: c3a0f1b8d2e4
Revises: b1a3f0c6d8a9
Create Date: 2026-01-31 00:00:01.000000

"""

from alembic import op


# revision identifiers, used by Alembic.
revision = "c3a0f1b8d2e4"
down_revision = "b1a3f0c6d8a9"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("expenses", schema=None) as batch_op:
        batch_op.drop_constraint("ck_expense_payee_type_allowed", type_="check")
        batch_op.create_check_constraint(
            "ck_expense_payee_type_allowed",
            "payee_type IN ('EMPLOYEE','SUPPLIER','CUSTOMER','PARTNER','WAREHOUSE','SHIPMENT','UTILITY','OTHER')",
        )


def downgrade():
    with op.batch_alter_table("expenses", schema=None) as batch_op:
        batch_op.drop_constraint("ck_expense_payee_type_allowed", type_="check")
        batch_op.create_check_constraint(
            "ck_expense_payee_type_allowed",
            "payee_type IN ('EMPLOYEE','SUPPLIER','PARTNER','UTILITY','OTHER')",
        )

