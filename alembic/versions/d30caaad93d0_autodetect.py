"""Autodetect?

Revision ID: d30caaad93d0
Revises: b246a8b733fa
Create Date: 2022-03-21 04:58:01.428483

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd30caaad93d0'
down_revision = 'b246a8b733fa'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('message', 'test')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('message', sa.Column('test', sa.VARCHAR(), autoincrement=False, nullable=True))
    # ### end Alembic commands ###