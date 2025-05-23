"""Add avatar to User

Revision ID: 5ecaaec32373
Revises: c7e6396cad46
Create Date: 2025-05-18 22:24:02.382949

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5ecaaec32373'
down_revision = 'c7e6396cad46'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                'avatar',
                sa.String(64),
                nullable=False,
                server_default='avatar.png'
            )
)


    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('avatar')

    # ### end Alembic commands ###
