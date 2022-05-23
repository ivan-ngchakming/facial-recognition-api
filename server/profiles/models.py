from sqlalchemy.dialects.postgresql import UUID

from ..core.model_base import ModelBaseMixin
from ..database import db


class Profile(db.Model, ModelBaseMixin):
    __tablename__ = "profile"

    name = db.Column(db.String(100))

    first_name = db.Column(db.String(100))
    middle_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    sex = db.Column(db.String(10))
    birth = db.Column(db.Date())

    def to_dict(self, *args, **kwargs):
        obj_dict = super().to_dict(*args, **kwargs)
        attributes = obj_dict.pop("attributes")
        obj_dict["attributes"] = dict(
            (attr["key"], attr["value"]) for attr in attributes
        )
        return obj_dict


class ProfileAttribute(db.Model, ModelBaseMixin):
    __tablename__ = "profile_attribute"
    __table_args__ = (
        db.UniqueConstraint("profile_id", "key", name="unique_key_per_profile"),
    )

    serialize_rules = ("-profile",)

    key = db.Column(db.String(30), nullable=False)
    value = db.Column(db.String, nullable=False, default="")

    profile_id = db.Column(UUID(as_uuid=True), db.ForeignKey("profile.id"))
    profile = db.relationship(
        "Profile",
        uselist=False,
        foreign_keys=profile_id,
        backref=db.backref("attributes"),
    )
