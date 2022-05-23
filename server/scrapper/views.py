from flask import Blueprint, request
from flask_api import status

from server.core.api_view import ApiView
from server.faces.models import Photo


class WebScrapeView(ApiView):
    """Endpoint for uploading web scrapping results"""

    def post(self):
        data = request.json

        if not data["url"]:
            return {"error": "Image URL not provided."}, status.HTTP_400_BAD_REQUEST

        obj = Photo()
        image_arr = Photo.get_image_from_url(data["url"])
        obj.create(image_arr)

        if len(obj.faces) == 0:
            return {"error": "No faces found in image"}, status.HTTP_204_NO_CONTENT

        # check for similar faces in database

        # create new profile or update existing profile

        # link faces to profile

        return {}, status.HTTP_200_OK

    @classmethod
    def register(cls, name: str, blueprint: Blueprint):
        return super().register(name, blueprint, methods=["POST"], pk_methods=[])


blueprint = Blueprint("scrapping", __name__, url_prefix="/scrapping")

WebScrapeView.register("upload", blueprint)
