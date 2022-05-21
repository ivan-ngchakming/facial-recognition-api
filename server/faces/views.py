import os
import uuid

from flask import Blueprint, Response, request
from flask_api import status
from PIL import Image
from server.faces.cosine_similarity import cosine_similarity
from werkzeug.datastructures import FileStorage

from ..config import Config
from ..core.api_view import ApiView
from .models import Face, Photo, Profile, ProfileAttribute


class FaceView(ApiView):
    model = Face


class ProfileView(ApiView):
    model = Profile


class ProfileAttributeView(ApiView):
    model = ProfileAttribute


class PhotosView(ApiView):
    model = Photo

    def post(self):
        data = request.json

        if "url" in data:
            if data["url"].startswith("/static/"):
                img = Image.open(Config.PROJECT_DIR + data["url"])
            else:
                img = Photo.get_image_arr_from_url(data["url"])

            obj = Photo()
            obj.create(img, url=data["url"])

            if len(obj.faces) > 0:
                self.db.session.add(obj)
                self.db.session.commit()

                return {"data": obj.to_dict()}

            return ({"error": "No faces found in picture."}, status.HTTP_204_NO_CONTENT)

        return {"error": "Image url not provided"}, status.HTTP_400_BAD_REQUEST


class ImageFileView(ApiView):
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
            name, blueprint, methods=["GET", "POST"], single_methods=["DELETE"]
        )


class FaceSearchView(ApiView):
    def get(self):
        return {}

    def put(self):
        data = request.json

        if not data["url"]:
            return {"error": "Image URL not provided."}, status.HTTP_400_BAD_REQUEST

        obj = Photo()
        image_arr = Photo.get_image_arr_from_url(data["url"])
        obj.create(image_arr)

        # calculate cosine distance to all face in database
        # TODO: use numpy vectorized operation to speed up consine distance calculation
        # TODO: Use k-NN algorithm to speed up search time
        faces = Face.query.all()
        results = []
        for face_to_search in obj.faces:
            current_results = []
            for face in faces:
                score = cosine_similarity(face.encoding, face_to_search.encoding)
                current_results.append({"face": face.to_dict(), "score": float(score)})
                current_results.sort(key=lambda x: x["score"], reverse=True)
            results.append(current_results)

        return {"data": results}

    @classmethod
    def register(cls, name: str, blueprint: Blueprint):
        return super().register(name, blueprint, methods=["GET", "PUT"])


blueprint = Blueprint("faces", __name__)

FaceView.register("faces", blueprint)
ProfileView.register("profiles", blueprint)
ProfileAttributeView.register("profile-attributes", blueprint)
PhotosView.register("photos", blueprint)
ImageFileView.register("photo-upload", blueprint)
FaceSearchView.register("face-search", blueprint)
