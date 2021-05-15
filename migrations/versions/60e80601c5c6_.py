"""empty message

Revision ID: 60e80601c5c6
Revises: 3be1e9fc15ae
Create Date: 2021-05-15 11:31:17.323906

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '60e80601c5c6'
down_revision = '3be1e9fc15ae'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('Shows_artist_id_fkey', 'Shows', type_='foreignkey')
    op.drop_constraint('Shows_venue_id_fkey', 'Shows', type_='foreignkey')
    op.create_foreign_key(None, 'Shows', 'Venue', ['venue_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'Shows', 'Artist', ['artist_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'Shows', type_='foreignkey')
    op.drop_constraint(None, 'Shows', type_='foreignkey')
    op.create_foreign_key('Shows_venue_id_fkey', 'Shows', 'Venue', ['venue_id'], ['id'])
    op.create_foreign_key('Shows_artist_id_fkey', 'Shows', 'Artist', ['artist_id'], ['id'])
    # ### end Alembic commands ###