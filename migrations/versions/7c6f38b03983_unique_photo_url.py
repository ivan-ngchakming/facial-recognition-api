"""unique photo url

Revision ID: 7c6f38b03983
Revises: 4195d0d39f4f
Create Date: 2022-05-23 23:30:46.276106

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "7c6f38b03983"
down_revision = "4195d0d39f4f"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "photo", "sha256_hash", existing_type=sa.VARCHAR(length=256), nullable=True
    )
    op.create_unique_constraint("photo_url_key", "photo", ["url"])
    op.create_unique_constraint("photo_sha256_hash_key", "photo", ["sha256_hash"])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint("photo_url_key", "photo", type_="unique")
    op.drop_constraint("photo_sha256_hash_key", "photo", type_="unique")
    op.alter_column(
        "photo", "sha256_hash", existing_type=sa.VARCHAR(length=256), nullable=False
    )
    # ### end Alembic commands ###
