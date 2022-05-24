"""add profile.source

Revision ID: 2ed48cf26ac5
Revises: fef17bd5b83b
Create Date: 2022-05-24 10:59:08.844424

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "2ed48cf26ac5"
down_revision = "fef17bd5b83b"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("profile", sa.Column("source", sa.String(length=50), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("profile", "source")
    # ### end Alembic commands ###
