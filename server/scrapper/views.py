from flask import Blueprint, request
from flask_api import status
from sqlalchemy.exc import IntegrityError

from ..core.api_view import ApiView
from .services import process_scrapped_data


class WebScrapeView(ApiView):
    """Endpoint for uploading web scrapping results"""

    def post(self):
        data = request.json

        if not data["url"]:
            return {"error": "Image URL not provided."}, status.HTTP_400_BAD_REQUEST

        try:
            _, new_profile_obj, existing_matched_profiles = process_scrapped_data(data)
        except IntegrityError as error:
            return {"error": str(error)}, status.HTTP_409_CONFLICT

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
