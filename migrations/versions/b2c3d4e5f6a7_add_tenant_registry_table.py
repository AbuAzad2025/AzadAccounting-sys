"""add tenant registry table

Revision ID: b2c3d4e5f6a7
Revises: a7b8c9d0e1f2
Create Date: 2026-05-21
"""
from alembic import op
import sqlalchemy as sa


revision = "b2c3d4e5f6a7"
down_revision = "a7b8c9d0e1f2"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "tenants",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("slug", sa.String(length=60), nullable=False),
        sa.Column("schema_name", sa.String(length=63), nullable=False),
        sa.Column("display_name", sa.String(length=200)),
        sa.Column("domain", sa.String(length=255)),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("slug", name="uq_tenants_slug"),
        sa.UniqueConstraint("schema_name", name="uq_tenants_schema_name"),
        sa.UniqueConstraint("domain", name="uq_tenants_domain"),
    )
    op.create_index("ix_tenants_slug", "tenants", ["slug"])
    op.create_index("ix_tenants_schema_name", "tenants", ["schema_name"])
    op.create_index("ix_tenants_is_active", "tenants", ["is_active"])


def downgrade():
    op.drop_index("ix_tenants_is_active", table_name="tenants")
    op.drop_index("ix_tenants_schema_name", table_name="tenants")
    op.drop_index("ix_tenants_slug", table_name="tenants")
    op.drop_table("tenants")
