"""init migrate

Revision ID: fef17bd5b83b
Revises:
Create Date: 2022-05-24 02:48:29.001701

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "fef17bd5b83b"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "photo",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "created_date",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column(
            "updated_date",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column("url", sa.String(), nullable=True),
        sa.Column("width", sa.Integer(), nullable=False),
        sa.Column("height", sa.Integer(), nullable=False),
        sa.Column("sha256_hash", sa.String(length=256), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("sha256_hash"),
        sa.UniqueConstraint("url"),
    )
    op.create_table(
        "profile",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "created_date",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column(
            "updated_date",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column("name", sa.String(length=100), nullable=True),
        sa.Column("first_name", sa.String(length=100), nullable=True),
        sa.Column("middle_name", sa.String(length=100), nullable=True),
        sa.Column("last_name", sa.String(length=100), nullable=True),
        sa.Column("sex", sa.String(length=10), nullable=True),
        sa.Column("birth", sa.Date(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "face",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "created_date",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column(
            "updated_date",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column("location", sa.PickleType(), nullable=False),
        sa.Column("landmarks", sa.PickleType(), nullable=False),
        sa.Column("encoding", sa.PickleType(), nullable=False),
        sa.Column("profile_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("photo_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(["photo_id"], ["photo.id"]),
        sa.ForeignKeyConstraint(["profile_id"], ["profile.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "profile_attribute",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "created_date",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column(
            "updated_date",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column("key", sa.String(length=30), nullable=False),
        sa.Column("value", sa.String(), nullable=False),
        sa.Column("profile_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(["profile_id"], ["profile.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("profile_id", "key", name="unique_key_per_profile"),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("profile_attribute")
    op.drop_table("face")
    op.drop_table("profile")
    op.drop_table("photo")
    # ### end Alembic commands ###
