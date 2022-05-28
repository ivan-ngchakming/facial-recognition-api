import hashlib
import uuid
from io import BytesIO
from typing import List

import cv2
import numpy as np
import requests
from PIL import Image
from werkzeug.datastructures import FileStorage

from ..faces.models import Face
from ..core.model_base import ModelBaseMixin
from ..database import db
from ..faces import face_app


class Photo(db.Model, ModelBaseMixin):
    __tablename__ = "photo"

    serialize_rules = ("-faces.photo",)

    url = db.Column(db.String, unique=True)
    width = db.Column(db.Integer, nullable=False)
    height = db.Column(db.Integer, nullable=False)
    sha256_hash = db.Column(db.String(256), unique=True)

    faces: List[Face] = db.relationship(
        "Face", uselist=True, cascade="all,delete,delete-orphan", overlaps="photo"
    )

    def create(self, image: Image, url: str = None, sha256_hash: str = None) -> "Photo":
        img_arr = np.array(image)

        self.width, self.height = image.size
        self.sha256_hash = sha256_hash or self.get_sha256_hash(image)

        if url is None:
            self.id = uuid.uuid4()
            self.url = f"/static/{self.id}.jpeg"
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

        return img_arr

    @staticmethod
    def get_sha256_hash(image: np.ndarray) -> str:
        return hashlib.sha256(image.tobytes()).hexdigest()

    @staticmethod
    def get_image_from_url(url: str) -> Image:
        res = requests.get(url)
        image = Image.open(BytesIO(res.content))
        return image

    @staticmethod
    def get_image_from_file_storage(file: FileStorage) -> Image:
        return Image.open(file)
