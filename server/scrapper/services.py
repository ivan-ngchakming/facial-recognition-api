from flask_api import status
from sqlalchemy import inspect

from server.profiles.controllers import update_profile_attributes

from ..database import db
from ..photos.models import Photo
from ..profiles.models import Profile
from ..faces.services import search_face


def process_scrapped_data(data: dict, threshold=0.6) -> tuple:
    """Process scrapped data and update database.

    1. Check if there are matching faces in the database
    2. Update existing profile if match, create new profile otherwise.

    Args:
        data (dict): url and other profile data

    Returns:
        Tuple(list, list): modified and created profiles
    """
    obj = Photo()
    image_arr = Photo.get_image_from_url(data["url"])
    obj.create(image_arr, data["url"])

    if len(obj.faces) == 0:
        return {"error": "No faces found in image"}, status.HTTP_204_NO_CONTENT

    # check for similar faces in database
    # TODO: allow threshold configuration via request params
    results = search_face(obj, threshold)

    matched = [False for _ in obj.faces]

    existing_matched_profiles = []
    for i, face in enumerate(obj.faces):
        # update existing profile
        if len(results[i]) > 0:
            face.profile = results[i][0]["face"].profile
            db.session.add(face)
            existing_matched_profiles.append(face.profile)
            matched[i] = True

            # TODO: deal with the case of score = 1 (ie. image already in database)

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
                    profile_obj = update_profile_attributes(
                        profile_obj, data["attributes"]
                    )
                continue
            if column.key in data:
                setattr(profile_obj, column.key, data[column.key])

        for i, face in enumerate(obj.faces):
            if not matched[i]:
                profile_obj.faces.append(face)

        db.session.add(profile_obj)

    db.session.add(obj)
    db.session.commit()

    return obj, new_profile_obj, existing_matched_profiles
