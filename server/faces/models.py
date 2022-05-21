import logging
import uuid

import cv2
import numpy as np
from sqlalchemy.orm import backref
from sqlalchemy_serializer import SerializerMixin

from ..database import db
from . import face_app

logger = logging.getLogger(__name__)

# pylint: disable=E1101


class Profile(db.Model, SerializerMixin):
    __tablename__ = "profile"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    # One-to-one relationship
    thumbnail_id = db.Column(db.Integer, db.ForeignKey("face.id"))
    thumbnail = db.relationship(
        "Face",
        uselist=False,
        foreign_keys=thumbnail_id,
        primaryjoin="Profile.thumbnail_id==Face.id",
        post_update=True,
    )

    @property
    def faces_count(self):
        return len(self.faces)

    def __repr__(self):
        return f"<Profile {self.name}({self.id})>"


class Face(db.Model, SerializerMixin):
    __tablename__ = "face"

    serialize_rules = ("-profile", "-photo.faces", "-encoding", "-landmarks")

    serialize_types = ((np.ndarray, lambda x: x.tolist()),)

    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.PickleType, nullable=False)
    landmarks = db.Column(db.PickleType, nullable=False)
    encoding = db.Column(db.PickleType, nullable=False)

    # Many-to-one relationship
    profile_id = db.Column(db.Integer, db.ForeignKey("profile.id"))
    profile = db.relationship(
        "Profile",
        uselist=False,
        backref=db.backref("faces", cascade="all,delete"),
        foreign_keys=profile_id,
    )

    # Many-to-one relationship
    photo_id = db.Column(db.Integer, db.ForeignKey("photo.id"))
    photo = db.relationship(
        "Photo",
        uselist=False,
        backref=backref("faces", cascade="all,delete,delete-orphan"),
    )

    def __repr__(self):
        if self.profile is None:
            return f"<Face of unknown person in Photo {self.photo.id} (id: {self.id})>"
        else:
            return f"<Face of {self.profile.name} in Photo {self.photo.id} (id: {self.id})>"


class Photo(db.Model, SerializerMixin):
    __tablename__ = "photo"

    serialize_rules = ("-faces.photo",)
    serialize_types = ((np.ndarray, lambda x: x.tolist()),)

    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String)
    width = db.Column(db.Integer, nullable=False)
    height = db.Column(db.Integer, nullable=False)

    def create(self, image, url=None) -> "Photo":
        img_arr = np.array(image)

        self.width, self.height = image.size

        if not url:
            self.url = f"/static/{uuid.uuid4()}.jpeg"
            cv2.imwrite(self.url, cv2.cvtColor(img_arr, cv2.COLOR_RGB2BGR))
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

    def __repr__(self):
        return f"<Photo {self.id} ({len(self.faces)} faces)>"
