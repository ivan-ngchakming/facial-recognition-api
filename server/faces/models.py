# pylint: disable=E1101

import hashlib
import logging
import uuid

import cv2
from ..config import Config
import numpy as np
from sqlalchemy.orm import backref
from sqlalchemy.dialects.postgresql import UUID

from ..core.model_base import ModelBaseMixin
from ..database import db
from . import face_app

logger = logging.getLogger(__name__)


class Profile(db.Model, ModelBaseMixin):
    __tablename__ = "profile"

    name = db.Column(db.String(100))

    first_name = db.Column(db.String(100))
    middle_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))

    sex = db.Column(db.String(10))

    # One-to-one relationship
    thumbnail_id = db.Column(UUID(as_uuid=True), db.ForeignKey("face.id"))
    thumbnail = db.relationship(
        "Face",
        uselist=False,
        foreign_keys=thumbnail_id,
        primaryjoin="Profile.thumbnail_id==Face.id",
        post_update=True,
    )


class ProfileAttribute(db.Model, ModelBaseMixin):
    __tablename__ = "profile_attribute"

    profile_id = db.Column(UUID(as_uuid=True), db.ForeignKey("profile.id"))
    profile = db.relationship(
        "Profile",
        uselist=False,
        foreign_keys=profile_id,
        backref=db.backref("attributes", cascade="all,delete"),
    )


class Face(db.Model, ModelBaseMixin):
    __tablename__ = "face"

    serialize_rules = ("-profile", "-photo.faces", "-encoding", "-landmarks")

    location = db.Column(db.PickleType, nullable=False)
    landmarks = db.Column(db.PickleType, nullable=False)
    encoding = db.Column(db.PickleType, nullable=False)

    # Many-to-one relationship
    profile_id = db.Column(UUID(as_uuid=True), db.ForeignKey("profile.id"))
    profile = db.relationship(
        "Profile",
        uselist=False,
        backref=db.backref("faces", cascade="all,delete"),
        foreign_keys=profile_id,
    )

    # Many-to-one relationship
    photo_id = db.Column(UUID(as_uuid=True), db.ForeignKey("photo.id"))
    photo = db.relationship(
        "Photo",
        uselist=False,
        backref=backref("faces", cascade="all,delete,delete-orphan"),
    )


class Photo(db.Model, ModelBaseMixin):
    __tablename__ = "photo"

    serialize_rules = ("-faces.photo",)

    url = db.Column(db.String)
    width = db.Column(db.Integer, nullable=False)
    height = db.Column(db.Integer, nullable=False)
    sha256_hash = db.Column(db.String, unique=True)

    def create(self, image, url=None) -> "Photo":
        img_arr = np.array(image)

        self.width, self.height = image.size
        self.sha256_hash = hashlib.sha256(image.tobytes()).hexdigest()

        if url is None:
            self.id = uuid.uuid4()
            self.url = f"/static/{self.id}.jpeg"
            cv2.imwrite(
                f"{Config.PROJECT_DIR}/public/{self.id}.jpeg",
                cv2.cvtColor(img_arr, cv2.COLOR_RGB2BGR),
            )
        else:
            self.url = url

        cvimg = cv2.cvtColor(img_arr, cv2.COLOR_RGB2BGR)
        arcfaces = face_app.get(cvimg)

        for arcface in arcfaces:
            face = Face(
                location=arcface.bbox,
                landmarks=arcface.landmark_2d_106,
                encoding=arcface.embedding,
            )
            self.faces.append(face)

        return self
