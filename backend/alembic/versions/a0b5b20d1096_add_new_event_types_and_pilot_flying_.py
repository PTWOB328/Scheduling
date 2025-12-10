"""Add new event types and pilot flying requirements

Revision ID: a0b5b20d1096
Revises: 7c58ba61c8d3
Create Date: 2025-12-10 06:46:49.401950

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a0b5b20d1096'
down_revision = '7c58ba61c8d3'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add new event types to the enum
    op.execute("ALTER TYPE eventtype ADD VALUE IF NOT EXISTS 'B2'")
    op.execute("ALTER TYPE eventtype ADD VALUE IF NOT EXISTS 'OB2'")
    op.execute("ALTER TYPE eventtype ADD VALUE IF NOT EXISTS 'OB3'")
    op.execute("ALTER TYPE eventtype ADD VALUE IF NOT EXISTS 'LOCAL'")
    op.execute("ALTER TYPE eventtype ADD VALUE IF NOT EXISTS 'MADDOG'")
    op.execute("ALTER TYPE eventtype ADD VALUE IF NOT EXISTS 'WST'")
    
    # Add flying requirements columns to pilots table
    op.add_column('pilots', sa.Column('b2_requirement', sa.Integer(), nullable=True, server_default='0'))
    op.add_column('pilots', sa.Column('t38_requirement', sa.Integer(), nullable=True, server_default='0'))
    op.add_column('pilots', sa.Column('wst_requirement', sa.Integer(), nullable=True, server_default='0'))


def downgrade() -> None:
    # Remove columns from pilots table
    op.drop_column('pilots', 'wst_requirement')
    op.drop_column('pilots', 't38_requirement')
    op.drop_column('pilots', 'b2_requirement')
    
    # Note: PostgreSQL doesn't support removing enum values easily
    # The enum values will remain but won't be used
