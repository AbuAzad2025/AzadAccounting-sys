"""expand gl_entries.ref length to 50

Revision ID: f6a7b8c9d0e1
Revises: e5f6a7b8c9d0
Create Date: 2026-02-15
"""
from alembic import op
import sqlalchemy as sa


revision = "f6a7b8c9d0e1"
down_revision = "e5f6a7b8c9d0"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("gl_entries", schema=None) as batch_op:
        batch_op.alter_column(
            "ref",
            existing_type=sa.String(20),
            type_=sa.String(50),
            existing_nullable=True,
        )


def downgrade():
    with op.batch_alter_table("gl_entries", schema=None) as batch_op:
        batch_op.alter_column(
            "ref",
            existing_type=sa.String(50),
            type_=sa.String(20),
            existing_nullable=True,
        )
