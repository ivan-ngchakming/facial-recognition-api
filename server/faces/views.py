from io import BytesIO

import requests
from flask import Blueprint, jsonify, request
from flask_api import status
from PIL import Image

from ..config import Config
from ..core.api_view import ApiView
from .models import Face, Photo, Profile


class FaceView(ApiView):
    model = Face


class ProfileView(ApiView):
    model = Profile


class PhotosView(ApiView):
    model = Photo

    def post(self):
        data = request.json

        if "url" in data:
            if data["url"].startswith("/static/"):
                img = Image.open(
                    Config.PROJECT_DIR + "/public/" + data["url"].split("/")[-1]
                )
            else:
                res = requests.get(data.url)
                img = Image.open(BytesIO(res.content))

            obj = Photo()
            obj.create(img, url=data["url"])

            if len(obj.faces) > 0:
                self.db.session.add(obj)
                self.db.session.commit()

                return jsonify({"data": obj.to_dict()})

            return (
                jsonify({"error": "No faces found in picture."}),
                status.HTTP_204_NO_CONTENT,
            )

        return jsonify({"error": "Image url not provided"}), status.HTTP_400_BAD_REQUEST


blueprint = Blueprint("faces", __name__)
FaceView.register("faces", blueprint)
ProfileView.register("profiles", blueprint)
PhotosView.register("photos", blueprint)
