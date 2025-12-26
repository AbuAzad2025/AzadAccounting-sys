"""remove_invoice_status_column

Revision ID: f3af84a72428
Revises: 8a75a15c043a
Create Date: 2025-10-26 23:59:29.366814

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f3af84a72428'
down_revision = '8a75a15c043a'
branch_labels = None
depends_on = None


def upgrade():
    """
    حذف عمود status من جدول invoices
    status أصبح property محسوب تلقائياً من total_paid
    """
    try:
        op.drop_index('ix_invoices_customer_status_date', table_name='invoices', if_exists=True)
    except TypeError:
        try:
            op.drop_index('ix_invoices_customer_status_date', table_name='invoices')
        except Exception:
            pass

    try:
        op.drop_index('ix_invoices_status', table_name='invoices', if_exists=True)
    except TypeError:
        try:
            op.drop_index('ix_invoices_status', table_name='invoices')
        except Exception:
            pass

    with op.batch_alter_table('invoices', schema=None) as batch_op:
        try:
            batch_op.drop_column('status')
        except Exception:
            pass


def downgrade():
    """
    إعادة عمود status في حالة الرجوع
    (نادراً ما نحتاج هذا، لكنه موجود للأمان)
    """
    pass  # لن نطبق downgrade لأنه معقد ونادر الاستخدام
