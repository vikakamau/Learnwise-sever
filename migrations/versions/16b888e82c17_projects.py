"""projects

Revision ID: 16b888e82c17
Revises: 648265397edf
Create Date: 2025-03-10 16:52:51.354481

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '16b888e82c17'
down_revision = '648265397edf'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('order_items')
    op.drop_table('projects')
    op.drop_table('orders')
    op.drop_table('users')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('username', sa.VARCHAR(length=100), nullable=False),
    sa.Column('email', sa.VARCHAR(length=120), nullable=False),
    sa.Column('password_hash', sa.VARCHAR(), nullable=False),
    sa.Column('is_admin', sa.BOOLEAN(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('username')
    )
    op.create_table('orders',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('user_id', sa.INTEGER(), nullable=True),
    sa.Column('name', sa.VARCHAR(length=100), nullable=False),
    sa.Column('email', sa.VARCHAR(length=100), nullable=False),
    sa.Column('phone', sa.VARCHAR(length=20), nullable=False),
    sa.Column('created_at', sa.DATETIME(), nullable=False),
    sa.Column('project_name', sa.VARCHAR(length=200), nullable=False),
    sa.Column('project_description', sa.VARCHAR(length=500), nullable=False),
    sa.Column('expected_duration', sa.VARCHAR(length=50), nullable=False),
    sa.Column('project_budget', sa.INTEGER(), nullable=False),
    sa.Column('file_url', sa.VARCHAR(length=255), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('projects',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('project_name', sa.VARCHAR(length=100), nullable=False),
    sa.Column('project_type', sa.VARCHAR(length=100), nullable=False),
    sa.Column('link_url', sa.VARCHAR(length=255), nullable=False),
    sa.Column('file_url', sa.VARCHAR(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('order_items',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('order_id', sa.INTEGER(), nullable=False),
    sa.Column('service_name', sa.VARCHAR(length=200), nullable=False),
    sa.Column('service_details', sa.VARCHAR(length=500), nullable=False),
    sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###
