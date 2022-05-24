from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..photos import Photo
    from ..profiles.models import Profile

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import deferred

from ..core.model_base import ModelBaseMixin
from ..database import db


class Face(db.Model, ModelBaseMixin):
    __tablename__ = "face"

    serialize_rules = (
        "-profile.faces",
        "-profile.thumbnail",
        "-photo.faces",
        "-encoding",
        "-landmarks",
    )

    location = deferred(db.Column(db.PickleType, nullable=False))
    landmarks = deferred(db.Column(db.PickleType, nullable=False))
    encoding = db.Column(db.PickleType, nullable=False)

    # Many-to-one relationship
    profile_id = db.Column(UUID(as_uuid=True), db.ForeignKey("profile.id"))
    profile: "Profile" = db.relationship(
        "Profile",
        uselist=False,
        backref=db.backref("faces", cascade="all,delete"),
        foreign_keys=profile_id,
    )

    # Many-to-one relationship
    photo_id = db.Column(UUID(as_uuid=True), db.ForeignKey("photo.id"))
    photo: "Photo" = db.relationship("Photo", uselist=False)
