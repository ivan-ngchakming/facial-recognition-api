from flask import Blueprint, request

from ..core.api_view import ApiView
from .controllers import update_profile_attributes
from .models import Profile, ProfileAttribute


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
            obj = update_profile_attributes(obj, data["attributes"])

        return super().post(obj=obj, excludes=["attributes"])


class ProfileAttributeView(ApiView):
    model = ProfileAttribute


blueprint = Blueprint("profiles", __name__)

ProfileView.register("profiles", blueprint)
ProfileAttributeView.register("profile-attributes", blueprint)
