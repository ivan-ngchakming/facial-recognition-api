from .models import ProfileAttribute


def update_profile_attributes(obj, attributes):
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
