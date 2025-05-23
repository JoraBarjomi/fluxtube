"""Fix subs

Revision ID: 9033f519a0c7
Revises: e4b329cf3a97
Create Date: 2025-05-19 21:41:49.934830

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9033f519a0c7'
down_revision = 'e4b329cf3a97'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('subscriptions',
    sa.Column('subscriber_id', sa.Integer(), nullable=False),
    sa.Column('author_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['author_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['subscriber_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('subscriber_id', 'author_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('subscriptions')
    # ### end Alembic commands ###
