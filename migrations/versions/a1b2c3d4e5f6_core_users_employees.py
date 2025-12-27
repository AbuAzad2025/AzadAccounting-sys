"""core_users_employees

Revision ID: a1b2c3d4e5f6
Revises:
Create Date: 2025-12-27 00:03:24.386686

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'roles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('description', sa.String(length=200), nullable=True),
        sa.Column('is_default', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    with op.batch_alter_table('roles', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_roles_name'), ['name'], unique=True)

    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('email', sa.String(length=120), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('role_id', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('(true)'), nullable=False),
        sa.Column('is_system_account', sa.Boolean(), server_default=sa.text('(false)'), nullable=False),
        sa.Column('last_login', sa.DateTime(), nullable=True),
        sa.Column('last_seen', sa.DateTime(), nullable=True),
        sa.Column('last_login_ip', sa.String(length=64), nullable=True),
        sa.Column('login_count', sa.Integer(), server_default=sa.text('0'), nullable=False),
        sa.Column('avatar_url', sa.String(length=500), nullable=True),
        sa.Column('notes_text', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_users_created_at'), ['created_at'], unique=False)
        batch_op.create_index(batch_op.f('ix_users_email'), ['email'], unique=True)
        batch_op.create_index(batch_op.f('ix_users_is_system_account'), ['is_system_account'], unique=False)
        batch_op.create_index(batch_op.f('ix_users_role_id'), ['role_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_users_updated_at'), ['updated_at'], unique=False)
        batch_op.create_index(batch_op.f('ix_users_username'), ['username'], unique=True)

    op.create_table(
        'employees',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('position', sa.String(length=100), nullable=True),
        sa.Column('salary', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('email', sa.String(length=120), nullable=True),
        sa.Column('hire_date', sa.Date(), nullable=True),
        sa.Column('bank_name', sa.String(length=100), nullable=True),
        sa.Column('account_number', sa.String(length=100), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('currency', sa.String(length=10), server_default=sa.text("'ILS'"), nullable=False),
        sa.Column('branch_id', sa.Integer(), nullable=False),
        sa.Column('site_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    with op.batch_alter_table('employees', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_employees_branch_id'), ['branch_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_employees_created_at'), ['created_at'], unique=False)
        batch_op.create_index(batch_op.f('ix_employees_email'), ['email'], unique=True)
        batch_op.create_index(batch_op.f('ix_employees_hire_date'), ['hire_date'], unique=False)
        batch_op.create_index(batch_op.f('ix_employees_name'), ['name'], unique=False)
        batch_op.create_index(batch_op.f('ix_employees_site_id'), ['site_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_employees_updated_at'), ['updated_at'], unique=False)


def downgrade():
    with op.batch_alter_table('employees', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_employees_updated_at'))
        batch_op.drop_index(batch_op.f('ix_employees_site_id'))
        batch_op.drop_index(batch_op.f('ix_employees_name'))
        batch_op.drop_index(batch_op.f('ix_employees_hire_date'))
        batch_op.drop_index(batch_op.f('ix_employees_email'))
        batch_op.drop_index(batch_op.f('ix_employees_created_at'))
        batch_op.drop_index(batch_op.f('ix_employees_branch_id'))
    op.drop_table('employees')

    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_users_username'))
        batch_op.drop_index(batch_op.f('ix_users_updated_at'))
        batch_op.drop_index(batch_op.f('ix_users_role_id'))
        batch_op.drop_index(batch_op.f('ix_users_is_system_account'))
        batch_op.drop_index(batch_op.f('ix_users_email'))
        batch_op.drop_index(batch_op.f('ix_users_created_at'))
    op.drop_table('users')

    with op.batch_alter_table('roles', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_roles_name'))
    op.drop_table('roles')

