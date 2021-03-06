"""empty message

Revision ID: 66c678a42e69
Revises: f49992cbae61
Create Date: 2020-03-28 14:21:21.622260

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '66c678a42e69'
down_revision = 'f49992cbae61'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('ih_house', sa.Column('max_day', sa.Integer(), nullable=True))
    op.add_column('ih_house', sa.Column('min_day', sa.Integer(), nullable=True))
    op.drop_column('ih_house', 'max_days')
    op.drop_column('ih_house', 'min_days')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('ih_house', sa.Column('min_days', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True))
    op.add_column('ih_house', sa.Column('max_days', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True))
    op.drop_column('ih_house', 'min_day')
    op.drop_column('ih_house', 'max_day')
    # ### end Alembic commands ###
