"""pwd reset token version

Revision ID: f3567fa0348b
Revises: e3f7c4d8bc13
Create Date: 2024-06-07 18:15:23.638497

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f3567fa0348b'
down_revision = 'e3f7c4d8bc13'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('pwd_reset_token_version', sa.Integer(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('pwd_reset_token_version')

    # ### end Alembic commands ###
