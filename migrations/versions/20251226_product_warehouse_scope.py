"""scope product uniqueness to warehouse

Revision ID: 20251226_product_wh_scope
Revises: 20251226_products_name_ci_unique
Create Date: 2025-12-26 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = "20251226_product_wh_scope"
down_revision = "20251226_products_name_ci_unique"
branch_labels = None
depends_on = None

def upgrade():
    # Add warehouse_id column
    op.add_column('products', sa.Column('warehouse_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_products_warehouse_id', 'products', 'warehouses', ['warehouse_id'], ['id'])
    
    # Drop global unique index
    op.drop_index('uq_products_name_ci', table_name='products')
    
    # Create per-warehouse unique index
    # (lower(name), warehouse_id) where warehouse_id IS NOT NULL
    op.create_index(
        'uq_products_name_wh_ci', 
        'products', 
        [sa.text('lower(name)'), 'warehouse_id'], 
        unique=True, 
        postgresql_where=sa.text('warehouse_id IS NOT NULL')
    )
    
    # Create global unique index (for products where warehouse_id IS NULL)
    op.create_index(
        'uq_products_name_global_ci', 
        'products', 
        [sa.text('lower(name)')], 
        unique=True, 
        postgresql_where=sa.text('warehouse_id IS NULL')
    )

def downgrade():
    op.drop_index('uq_products_name_global_ci', table_name='products')
    op.drop_index('uq_products_name_wh_ci', table_name='products')
    op.create_index('uq_products_name_ci', 'products', [sa.text('lower(name)')], unique=True)
    op.drop_constraint('fk_products_warehouse_id', 'products', type_='foreignkey')
    op.drop_column('products', 'warehouse_id')
