"""update photo hash column type

Revision ID: 4195d0d39f4f
Revises: 43e4f7a14985
Create Date: 2022-05-22 14:39:19.272670

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "4195d0d39f4f"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Rename old column to a tmp name
    op.alter_column("photo", "sha256_hash", new_column_name="sha256_hash_old")

    # add new column
    op.add_column("photo", sa.Column("sha256_hash", sa.String(length=256)))
    op.execute("UPDATE photo SET sha256_hash=sha256_hash_old")
    op.alter_column("photo", "sha256_hash", nullable=False)

    # Drop old column
    op.drop_column("photo", "sha256_hash_old")


def downgrade():
    op.alter_column("photo", "sha256_hash", new_column_name="sha256_hash_new")

    op.add_column(
        "photo",
        sa.Column("sha256_hash", sa.VARCHAR(), autoincrement=False, nullable=True),
    )
    op.execute("UPDATE photo SET sha256_hash=sha256_hash_new")

    op.create_unique_constraint("photo_sha256_hash_key", "photo", ["sha256_hash"])

    op.drop_column("photo", "sha256_hash_new")
