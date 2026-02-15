"""expand accounts.code length to 50

Revision ID: e5f6a7b8c9d0
Revises: d4e5f6a7b8c9
Create Date: 2026-02-14

بعض أكواد الحسابات في النظام (مثل 6200_INCOME_TAX_EXPENSE) أطول من 20 حرفاً.
"""
from alembic import op
import sqlalchemy as sa


revision = "e5f6a7b8c9d0"
down_revision = "d4e5f6a7b8c9"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("accounts", schema=None) as batch_op:
        batch_op.alter_column(
            "code",
            existing_type=sa.String(20),
            type_=sa.String(50),
            existing_nullable=False,
        )


def downgrade():
    with op.batch_alter_table("accounts", schema=None) as batch_op:
        batch_op.alter_column(
            "code",
            existing_type=sa.String(50),
            type_=sa.String(20),
            existing_nullable=False,
        )
