import uuid

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy_serializer import SerializerMixin
import numpy as np

from ..database import db


class ModelBaseMixin(SerializerMixin):

    serialize_types = ((np.ndarray, lambda x: x.tolist()),)

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_date = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_date = db.Column(
        db.DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
