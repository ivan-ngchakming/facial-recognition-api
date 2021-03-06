import os
import uuid

from flask import Blueprint, Response, request
from flask_api import status
from PIL import Image
import numpy as np
from werkzeug.datastructures import FileStorage

from ..config import Config
from ..core.api_view import ApiView
from .models import Photo


class PhotosView(ApiView):
    model = Photo

    def post(self):
        data = request.json

        if "url" in data:
            if data["url"].startswith("/static/"):
                img = Image.open(Config.PUBLIC_DIR + data["url"])
            else:
                img = Photo.get_image_from_url(data["url"])

            sha256_hash = Photo.get_sha256_hash(np.array(img))

            obj = Photo.query.filter(Photo.sha256_hash == sha256_hash).first()
            if obj:
                return (
                    {"error": "Photo already exist.", "data": obj.to_dict()},
                    status.HTTP_409_CONFLICT,
                )

            obj = Photo()
            obj.create(img, url=data["url"], sha256_hash=sha256_hash)

            if len(obj.faces) > 0:
                self.db.session.add(obj)
                self.db.session.commit()

                return obj.to_dict()

            return ({"error": "No faces found in picture."}, status.HTTP_204_NO_CONTENT)

        return {"error": "Image url not provided"}, status.HTTP_400_BAD_REQUEST


class ImageFileView(ApiView):
    """Image file hosting service

    TODO: Set expiration date on files and clean up with cron jobs
    TODO: Create Image file model to persist image file meta data to database
    """

    upload_folder = Config.UPLOAD_FOLDER
    allowed_extensions = Config.ALLOWED_EXTENSIONS

    def get(self) -> Response:
        return {}

    def post(self) -> Response:
        """Upload a new image to `/public` directory of the project"""

        # check if the post request has the file part
        if "file" not in request.files:
            return {"error": "File not provided"}, status.HTTP_400_BAD_REQUEST

        file = request.files["file"]
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == "" or not file:
            return {"error": "File not selected"}, status.HTTP_400_BAD_REQUEST

        if not self.allowed_file(file.filename):
            return (
                {"error": f"File extension {self.get_file_extension(file.filename)}"},
                status.HTTP_400_BAD_REQUEST,
            )

        filename = self.upload(file)
        return {"url": f"/static/{filename}"}, status.HTTP_201_CREATED

    def delete(self, filename: str) -> Response:
        full_filename = self.upload_folder + "/" + filename

        if os.path.exists(full_filename):
            os.remove(full_filename)
            return {"success": "File successfully removed"}, status.HTTP_200_OK
        else:
            return {"error": "File does not exist"}, status.HTTP_204_NO_CONTENT

    @staticmethod
    def get_file_extension(filename):
        return filename.rsplit(".", 1)[1].lower()

    @classmethod
    def allowed_file(cls, filename):
        return (
            "." in filename
            and cls.get_file_extension(filename) in cls.allowed_extensions
        )

    @classmethod
    def upload(cls, file: FileStorage) -> str:
        filename = f"{uuid.uuid4()}.{cls.get_file_extension(file.filename)}"
        file.save(os.path.join(cls.upload_folder, filename))
        return filename

    @classmethod
    def register(cls, name: str, blueprint: Blueprint):
        return super().register(
            name, blueprint, methods=["GET", "POST"], pk_methods=["DELETE"]
        )


blueprint = Blueprint("photos", __name__, url_prefix="/photos")

PhotosView.register("", blueprint)
ImageFileView.register("upload", blueprint)
