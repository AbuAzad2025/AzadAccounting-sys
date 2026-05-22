"""مواءمة GRN مع الموديل

Revision ID: l2m3n4o8
Revises: k1l2m3n4o7
"""
from alembic import op
import sqlalchemy as sa


revision = "l2m3n4o8"
down_revision = "k1l2m3n4o7"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("goods_receipt_lines", schema=None) as batch_op:
        batch_op.add_column(sa.Column("created_at", sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column("updated_at", sa.DateTime(), nullable=True))

    with op.batch_alter_table("goods_receipts", schema=None) as batch_op:
        batch_op.drop_column("created_by")
        batch_op.drop_column("updated_by")


def downgrade():
    with op.batch_alter_table("goods_receipts", schema=None) as batch_op:
        batch_op.add_column(sa.Column("created_by", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("updated_by", sa.Integer(), nullable=True))
    with op.batch_alter_table("goods_receipt_lines", schema=None) as batch_op:
        batch_op.drop_column("updated_at")
        batch_op.drop_column("created_at")
