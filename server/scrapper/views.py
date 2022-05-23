from flask import Blueprint, request
from flask_api import status
from sqlalchemy import inspect
from server.core.api_view import ApiView
from server.faces.models import Photo, Profile
from server.faces.views import ProfileView
from server.search.services import search_face


class WebScrapeView(ApiView):
    """Endpoint for uploading web scrapping results"""

    def post(self):
        data = request.json

        if not data["url"]:
            return {"error": "Image URL not provided."}, status.HTTP_400_BAD_REQUEST

        obj = Photo()
        image_arr = Photo.get_image_from_url(data["url"])
        obj.create(image_arr, data["url"])

        if len(obj.faces) == 0:
            return {"error": "No faces found in image"}, status.HTTP_204_NO_CONTENT

        # check for similar faces in database
        # TODO: allow threshold configuration via request params
        results = search_face(obj, 0.5)

        matched = [False for _ in obj.faces]

        existing_matched_profiles = []
        for i, face in enumerate(obj.faces):
            # update existing profile
            if len(results[i]) > 0:
                face.profile = results[i][0]["face"].profile
                self.db.session.add(face)
                existing_matched_profiles.append(face.profile)
                matched[i] = True

        # create new profile
        new_profile_obj = None

        profile_objs = []
        if False in matched:
            new_profile_obj = Profile()
            profile_objs.append(new_profile_obj)

        for profile_obj in profile_objs:
            for column in inspect(Profile).attrs:
                if column.key == "attributes":
                    if "attributes" in data:
                        profile_obj = ProfileView.update_attributes(
                            profile_obj, data["attributes"]
                        )
                    continue
                if column.key in data:
                    setattr(profile_obj, column.key, data[column.key])

            for i, face in enumerate(obj.faces):
                if not matched[i]:
                    profile_obj.faces.append(face)

            self.db.session.add(profile_obj)

        self.db.session.add(obj)
        self.db.session.commit()

        if new_profile_obj:
            new_profile_obj = new_profile_obj.to_dict()

        return (
            {
                "existing_matches": [
                    obj.to_dict() for obj in existing_matched_profiles
                ],
                "created": new_profile_obj,
            },
            status.HTTP_200_OK,
        )

    @classmethod
    def register(cls, name: str, blueprint: Blueprint):
        return super().register(name, blueprint, methods=["POST"], pk_methods=[])


blueprint = Blueprint("scrapping", __name__, url_prefix="/scrapping")

WebScrapeView.register("upload", blueprint)
