"""empty message

Revision ID: 23f3f39fcbd4
Revises: 03d7ffd5d64e
Create Date: 2021-05-13 14:59:03.449163

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '23f3f39fcbd4'
down_revision = '03d7ffd5d64e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Shows', sa.Column('start_date', sa.Date(), nullable=True))
    op.drop_column('Shows', 'date')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Shows', sa.Column('date', sa.DATE(), autoincrement=False, nullable=True))
    op.drop_column('Shows', 'start_date')
    # ### end Alembic commands ###
