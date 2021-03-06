"""Added email to user model

Revision ID: 170ad6790cf2
Revises: 
Create Date: 2022-01-13 21:13:09.974654

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '170ad6790cf2'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('email', sa.String(length=96), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'email')
    # ### end Alembic commands ###
