import json

from dateutil.parser import parse
from flask import Blueprint, Response, jsonify, request
from flask.views import MethodView
from flask_sqlalchemy import Model
from sqlalchemy.sql import sqltypes

from ..database import db


class ApiView(MethodView):
    """Base class for Rest API view"""

    db = db
    model = None

    def __init__(self, model=None) -> None:
        super().__init__()
        if model:
            self.model = model

    def get(self, obj_id: str = None) -> Response:
        """Get list of objects or one by object id

        Args:
            obj_id (str, optional): object id. Defaults to None.

        Returns:
            Response: response object
        """
        if obj_id:
            return self.model.query.get(obj_id).to_dict()

        return jsonify([obj.to_dict() for obj in self.model.query.all()])

    def post(self) -> Response:
        if request.is_json:
            data = request.json
            obj = self.model()
            obj = self._update_obj(obj, data)

            self.db.session.add(obj)
            self.db.session.commit()

            return jsonify(obj.to_dict())

    def patch(self, obj_id: str = None) -> Response:
        data = request.json
        if not obj_id:
            obj = self.model()
        else:
            obj = self.model.query.get(obj_id)

        obj = self._update_obj(obj, data)

        self.db.session.add(obj)
        self.db.session.commit()

        return jsonify(obj.to_dict())

    def _update_obj(self, obj: Model, data: dict) -> Model:
        for k, v in data.items():
            if hasattr(obj, k):
                if isinstance(v, dict):
                    obj = self._update_obj(getattr(obj, k), v)
                    continue

                column_type = type(getattr(obj.__table__.columns, k).type)
                if column_type in [sqltypes.DateTime, sqltypes.Date, sqltypes.Time]:
                    v = self._str_to_date_time(column_type, v)
                if column_type == sqltypes.Boolean:
                    if str(v).lower() in ["1", "true", "yes"]:
                        v = True
                    elif str(v).lower() in ["0", "false", "no"]:
                        v = False
                    else:
                        v = None
                if isinstance(v, dict) or isinstance(v, list):
                    v = json.dumps(v) if v else None
                setattr(obj, k, v)
        return obj

    @staticmethod
    def _str_to_date_time(column_type: type, value: any) -> any:
        if value:
            if column_type == sqltypes.DateTime:
                value = parse(value)
            if column_type == sqltypes.Date:
                value = parse(value).date()
            if column_type == sqltypes.Time:
                value = parse(value).time()
        return value

    @classmethod
    def register(cls, name: str, blueprint: Blueprint):
        """Register view to flask app

        Args:
            name (str): name of view
            blueprint (Blueprint): blueprint object to register to
        """
        view_func = cls.as_view(name)
        blueprint.add_url_rule(
            view_func=view_func, rule=f"/{name}/", methods=["GET", "POST", "PATCH"]
        )
        blueprint.add_url_rule(
            view_func=view_func, rule=f"/{name}/<int:id>", methods=["GET", "PATCH"]
        )
