"""increase_customer_password_hash_length

Revision ID: c0f7a1b2c3d4
Revises: 84a17762f7c4
Create Date: 2025-12-24 12:06:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "c0f7a1b2c3d4"
down_revision = "84a17762f7c4"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("customers") as batch_op:
        batch_op.alter_column(
            "password_hash",
            existing_type=sa.String(length=128),
            type_=sa.String(length=512),
            existing_nullable=True,
        )


def downgrade():
    with op.batch_alter_table("customers") as batch_op:
        batch_op.alter_column(
            "password_hash",
            existing_type=sa.String(length=512),
            type_=sa.String(length=128),
            existing_nullable=True,
        )

