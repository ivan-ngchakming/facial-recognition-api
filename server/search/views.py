from flask import Blueprint, request
from flask_api import status
from server.search.services import search_face

from ..core.api_view import ApiView
from ..faces.models import Photo


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

        search_results = search_face(obj)

        for results in search_results:
            if len(results) > 10:
                results = results[:10]

            for result in results:
                result["face"] = result["face"].to_dict()

        return search_results

    @classmethod
    def register(cls, name: str, blueprint: Blueprint):
        return super().register(name, blueprint, methods=["GET", "PUT"], pk_methods=[])


blueprint = Blueprint("search", __name__, url_prefix="/search")

FaceSearchView.register("face", blueprint)
