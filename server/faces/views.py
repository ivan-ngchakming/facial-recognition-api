import os
import uuid

from flask import Blueprint, Response, request
from flask_api import status
from PIL import Image
import numpy as np
from server.faces.cosine_similarity import cosine_similarity
from werkzeug.datastructures import FileStorage

from ..config import Config
from ..core.api_view import ApiView
from .models import Face, Photo, Profile, ProfileAttribute


class FaceView(ApiView):
    model = Face


class ProfileView(ApiView):
    model = Profile

    filterable_fields = ("name",)

    def post(self):
        data = request.json

        obj: Profile = self.model()

        if "attributes" in data:
            obj.attributes = [
                ProfileAttribute(key=key, value=value)
                for key, value in data["attributes"].items()
            ]

        return super().post(obj=obj, excludes=["attributes"])

    def patch(self, id=None):
        data = request.json

        if not id:
            obj = self.model()
        else:
            obj = self.model.query.get(id)

        if "attributes" in data:
            for key, value in data["attributes"].items():
                updated = False
                for attribute_obj in obj.attributes:
                    if key == attribute_obj.key:
                        attribute_obj.value = value
                        updated = True
                        break
                if not updated:
                    obj.attributes.append(ProfileAttribute(key=key, value=value))

        return super().post(obj=obj, excludes=["attributes"])


class ProfileAttributeView(ApiView):
    model = ProfileAttribute


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


class FaceSearchView(ApiView):
    def get(self):
        url = request.args.get("url")

        if not url:
            return {"error": "Image URL not provided."}, status.HTTP_400_BAD_REQUEST

        return self.search(url), status.HTTP_200_OK

    def put(self):
        data = request.json

        if not data["url"]:
            return {"error": "Image URL not provided."}, status.HTTP_400_BAD_REQUEST

        return self.search(data["url"]), status.HTTP_200_OK

    @staticmethod
    def search(url):
        obj = Photo()
        image_arr = Photo.get_image_from_url(url)
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
                
                if score > 0.1:
                    current_results.append({"face": face, "score": float(score)})
                
            current_results.sort(key=lambda x: x["score"], reverse=True)
            
            if len(current_results) > 10:
                current_results = current_results[:10]
                
            for current_result in current_results:
                current_result["face"] = current_result["face"].to_dict()

            results.append(current_results)

        return results

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
