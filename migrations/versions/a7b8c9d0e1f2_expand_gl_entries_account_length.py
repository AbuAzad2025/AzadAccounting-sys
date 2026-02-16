"""expand gl_entries.account length to 50

Revision ID: a7b8c9d0e1f2
Revises: f6a7b8c9d0e1
Create Date: 2026-02-16
"""

from alembic import op
import sqlalchemy as sa


revision = "a7b8c9d0e1f2"
down_revision = "f6a7b8c9d0e1"
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    if conn.dialect.name == "postgresql":
        cur_len = conn.execute(
            sa.text(
                """
                SELECT character_maximum_length
                FROM information_schema.columns
                WHERE table_schema='public' AND table_name='gl_entries' AND column_name='account'
                """
            )
        ).scalar()
        try:
            cur_len_i = int(cur_len) if cur_len is not None else None
        except Exception:
            cur_len_i = None
        if cur_len_i is None or cur_len_i < 50:
            op.execute(sa.text("ALTER TABLE public.gl_entries ALTER COLUMN account TYPE VARCHAR(50)"))
        return

    with op.batch_alter_table("gl_entries", schema=None) as batch_op:
        batch_op.alter_column(
            "account",
            existing_type=sa.String(20),
            type_=sa.String(50),
            existing_nullable=False,
        )


def downgrade():
    conn = op.get_bind()
    if conn.dialect.name == "postgresql":
        cur_len = conn.execute(
            sa.text(
                """
                SELECT character_maximum_length
                FROM information_schema.columns
                WHERE table_schema='public' AND table_name='gl_entries' AND column_name='account'
                """
            )
        ).scalar()
        try:
            cur_len_i = int(cur_len) if cur_len is not None else None
        except Exception:
            cur_len_i = None
        if cur_len_i is not None and cur_len_i > 20:
            op.execute(sa.text("ALTER TABLE public.gl_entries ALTER COLUMN account TYPE VARCHAR(20)"))
        return

    with op.batch_alter_table("gl_entries", schema=None) as batch_op:
        batch_op.alter_column(
            "account",
            existing_type=sa.String(50),
            type_=sa.String(20),
            existing_nullable=False,
        )

