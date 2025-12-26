"""allow_direct_payments_to_partners_suppliers

Revision ID: 7de7e996a21e
Revises: f3af84a72428
Create Date: 2025-10-27 01:12:11.366814

تعديل constraint للسماح بالدفعات المباشرة للشركاء والموردين
في الحياة العملية: دفعة مباشرة للشريك/المورد = تسوية حساب
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7de7e996a21e'
down_revision = 'f3af84a72428'
branch_labels = None
depends_on = None


def upgrade():
    """
    تعديل ck_payment_one_target من = 1 إلى <= 1
    للسماح بالدفعات المباشرة (بدون ربط بفاتورة/مبيعة/الخ)
    """
    try:
        op.drop_constraint('ck_payment_one_target', 'payments', type_='check')
    except Exception:
        pass

    op.create_check_constraint(
        'ck_payment_one_target',
        'payments',
        """(
            (CASE WHEN customer_id IS NOT NULL THEN 1 ELSE 0 END) +
            (CASE WHEN supplier_id IS NOT NULL THEN 1 ELSE 0 END) +
            (CASE WHEN partner_id IS NOT NULL THEN 1 ELSE 0 END) +
            (CASE WHEN shipment_id IS NOT NULL THEN 1 ELSE 0 END) +
            (CASE WHEN expense_id IS NOT NULL THEN 1 ELSE 0 END) +
            (CASE WHEN loan_settlement_id IS NOT NULL THEN 1 ELSE 0 END) +
            (CASE WHEN sale_id IS NOT NULL THEN 1 ELSE 0 END) +
            (CASE WHEN invoice_id IS NOT NULL THEN 1 ELSE 0 END) +
            (CASE WHEN preorder_id IS NOT NULL THEN 1 ELSE 0 END) +
            (CASE WHEN service_id IS NOT NULL THEN 1 ELSE 0 END)
        ) <= 1
        )""",
    )


def downgrade():
    """الرجوع للقيد القديم (نادراً ما يُستخدم)"""
    pass
