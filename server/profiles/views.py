from flask import Blueprint, request
from ..core.api_view import ApiView
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
            obj = self.update_attributes(obj, data["attributes"])

        return super().post(obj=obj, excludes=["attributes"])

    @staticmethod
    def update_attributes(obj, attributes):
        for key, value in attributes.items():
            updated = False
            for attribute_obj in obj.attributes:
                if key == attribute_obj.key:
                    attribute_obj.value = value
                    updated = True
                    break
            if not updated:
                obj.attributes.append(ProfileAttribute(key=key, value=value))

        return obj


class ProfileAttributeView(ApiView):
    model = ProfileAttribute


blueprint = Blueprint("profiles", __name__)

ProfileView.register("profiles", blueprint)
ProfileAttributeView.register("profile-attributes", blueprint)
