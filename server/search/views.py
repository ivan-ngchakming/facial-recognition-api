from flask import Blueprint, current_app, request, abort, make_response
from flask_api import status
from requests.exceptions import MissingSchema
from sqlalchemy.exc import IntegrityError

from ..core.api_view import ApiView
from ..faces.models import Photo
from ..scrapper.services import process_scrapped_data
from .services import search_face


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

    @classmethod
    def search(cls, url: str):
        if url.startswith("/static/"):
            obj = Photo()
            try:
                image_arr = Photo.get_image_from_url(url)
            except MissingSchema as error:
                abort(make_response({"error": str(error)}, status.HTTP_400_BAD_REQUEST))
            obj.create(image_arr)
        else:
            try:
                obj, _, _ = process_scrapped_data({"url": url})
            except IntegrityError:
                current_app.logger.warn(
                    "Attempted to insert an image already exist in the database: " + url
                )
                cls.db.session.rollback()
                obj = Photo.query.filter(Photo.url == url).first()
            except MissingSchema as error:
                abort(make_response({"error": str(error)}, status.HTTP_400_BAD_REQUEST))

        search_results = search_face(obj, exclude_urls=[url])

        for i, results in enumerate(search_results):
            if len(results) > 10:
                search_results[i] = results[:10]

            for j, result in enumerate(search_results[i]):
                search_results[i][j]["face"] = result["face"].to_dict()

        return search_results

    @classmethod
    def register(cls, name: str, blueprint: Blueprint):
        return super().register(name, blueprint, methods=["GET", "PUT"], pk_methods=[])


blueprint = Blueprint("search", __name__, url_prefix="/search")

FaceSearchView.register("face", blueprint)
