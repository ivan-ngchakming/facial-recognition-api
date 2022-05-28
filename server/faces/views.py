from flask import Blueprint, abort, current_app, make_response, request
from flask_api import status
from requests.exceptions import MissingSchema
from sqlalchemy.exc import IntegrityError
from werkzeug.datastructures import FileStorage

from server.config import Config

from ..core.api_view import ApiView
from ..photos.models import Photo
from ..scrapper.services import process_scrapped_data
from .models import Face
from .services import search_face


class FaceView(ApiView):
    model = Face


class FaceSearchView(ApiView):
    allowed_extensions = Config.ALLOWED_EXTENSIONS

    def get(self):
        url = request.args.get("url")

        if not url:
            return {"error": "Image URL not provided."}, status.HTTP_400_BAD_REQUEST

        return self.search(url), status.HTTP_200_OK

    def post(self):
        file = request.files["file"]
        if file.filename != "" and file and self.allowed_file(file.filename):
            return self.search(file), status.HTTP_200_OK

        return {"error": "Image URL not provided."}, status.HTTP_400_BAD_REQUEST

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
    def search(cls, source):
        if isinstance(source, FileStorage):
            obj = Photo()
            image_arr = Photo.get_image_from_file_storage(source)
            obj.create(image_arr)
        elif source.startswith("/static/"):
            obj = Photo()
            try:
                image_arr = Photo.get_image_from_url(source)
            except MissingSchema as error:
                abort(make_response({"error": str(error)}, status.HTTP_400_BAD_REQUEST))
            obj.create(image_arr)
        else:
            try:
                obj, _, _ = process_scrapped_data({"url": source})
            except IntegrityError:
                current_app.logger.warn(
                    "Attempted to insert an image already exist in the database: "
                    + source
                )
                cls.db.session.rollback()
                obj = Photo.query.filter(Photo.url == source).first()
            except MissingSchema as error:
                abort(make_response({"error": str(error)}, status.HTTP_400_BAD_REQUEST))

        search_results = search_face(obj, exclude_urls=[source])

        for i, results in enumerate(search_results):
            if len(results) > 10:
                search_results[i] = results[:10]

            for j, result in enumerate(search_results[i]):
                search_results[i][j]["face"] = result["face"].to_dict()

        return search_results

    @classmethod
    def register(cls, name: str, blueprint: Blueprint):
        return super().register(name, blueprint, methods=["GET", "POST"], pk_methods=[])


blueprint = Blueprint("faces", __name__, url_prefix="/faces")

FaceView.register("", blueprint)
FaceSearchView.register("search", blueprint)
