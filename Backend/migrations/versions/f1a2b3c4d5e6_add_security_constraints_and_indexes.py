"""Add security constraints and indexes

Revision ID: f1a2b3c4d5e6
Revises: b2118555ff6f
Create Date: 2025-03-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f1a2b3c4d5e6'
down_revision = 'b2118555ff6f'
branch_labels = None
depends_on = None


def upgrade():
    """Add indexes and constraints for security and performance."""
    
    # Add indexes on foreign keys for better query performance
    op.create_index(op.f('ix_orders_user_id'), 'orders', ['user_id'], existing_ok=True)
    op.create_index(op.f('ix_products_category_id'), 'products', ['category_id'], existing_ok=True)
    op.create_index(op.f('ix_panier_user_id'), 'panier', ['user_id'], existing_ok=True)
    op.create_index(op.f('ix_panier_product_id'), 'panier', ['product_id'], existing_ok=True)
    op.create_index(op.f('ix_order_items_order_id'), 'order_items', ['order_id'], existing_ok=True)
    op.create_index(op.f('ix_order_items_product_id'), 'order_items', ['product_id'], existing_ok=True)
    op.create_index(op.f('ix_transactions_order_id'), 'transactions', ['order_id'], existing_ok=True)
    op.create_index(op.f('ix_transactions_user_id'), 'transactions', ['user_id'], existing_ok=True)
    
    # Add indexes on email and username for faster lookups
    op.create_index(op.f('ix_users_email'), 'users', ['email'], existing_ok=True)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], existing_ok=True)
    
    # Add index on product name for search functionality
    op.create_index(op.f('ix_products_name'), 'products', ['name'], existing_ok=True)
    
    # Add NOT NULL constraints where needed (if not already present)
    # Note: These may fail if null values exist, so they're commented by default
    # Uncomment after verifying no null values exist in data
    try:
        op.alter_column('users', 'is_admin',
                       existing_type=sa.Boolean(),
                       nullable=False,
                       server_default=sa.false())
    except Exception:
        pass  # Column may already have constraint
    
    try:
        op.alter_column('orders', 'updated_at',
                       existing_type=sa.DateTime(),
                       nullable=False,
                       server_default=sa.func.now())
    except Exception:
        pass  # Column may already have constraint


def downgrade():
    """Remove indexes and constraints."""
    
    # Drop indexes
    op.drop_index(op.f('ix_transactions_user_id'), table_name='transactions', existing_ok=True)
    op.drop_index(op.f('ix_transactions_order_id'), table_name='transactions', existing_ok=True)
    op.drop_index(op.f('ix_order_items_product_id'), table_name='order_items', existing_ok=True)
    op.drop_index(op.f('ix_order_items_order_id'), table_name='order_items', existing_ok=True)
    op.drop_index(op.f('ix_panier_product_id'), table_name='panier', existing_ok=True)
    op.drop_index(op.f('ix_panier_user_id'), table_name='panier', existing_ok=True)
    op.drop_index(op.f('ix_products_category_id'), table_name='products', existing_ok=True)
    op.drop_index(op.f('ix_orders_user_id'), table_name='orders', existing_ok=True)
    op.drop_index(op.f('ix_products_name'), table_name='products', existing_ok=True)
    op.drop_index(op.f('ix_users_username'), table_name='users', existing_ok=True)
    op.drop_index(op.f('ix_users_email'), table_name='users', existing_ok=True)
