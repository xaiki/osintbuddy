"""Modified search_category

Revision ID: a13bfde2b847
Revises: 233ea95fb6d2
Create Date: 2021-08-28 05:07:33.412821

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a13bfde2b847'
down_revision = '233ea95fb6d2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('cse', sa.Column('search_category_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'cse', 'search_category', ['search_category_id'], ['id'])
    op.drop_constraint('search_category_cse_id_fkey', 'search_category', type_='foreignkey')
    op.drop_column('search_category', 'cse_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('search_category', sa.Column('cse_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.create_foreign_key('search_category_cse_id_fkey', 'search_category', 'cse', ['cse_id'], ['id'])
    op.drop_constraint(None, 'cse', type_='foreignkey')
    op.drop_column('cse', 'search_category_id')
    # ### end Alembic commands ###