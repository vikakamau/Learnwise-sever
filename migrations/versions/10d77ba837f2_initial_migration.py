"""Initial migration

Revision ID: 10d77ba837f2
Revises: caba3f64c8d3
Create Date: 2025-03-08 00:08:24.988715

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '10d77ba837f2'
down_revision = 'caba3f64c8d3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('name', sa.VARCHAR(length=100), nullable=False),
    sa.Column('email', sa.VARCHAR(length=100), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    # ### end Alembic commands ###
