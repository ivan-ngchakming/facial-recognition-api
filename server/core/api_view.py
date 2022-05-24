import json

from dateutil.parser import parse
from flask import Blueprint, Response, request
from flask.views import MethodView
from flask_sqlalchemy import Model
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import sqltypes
from flask_api import status
from sqlalchemy.orm.collections import InstrumentedList
from sqlalchemy.orm import Query

from ..database import db


class ApiView(MethodView):
    """Base class for Rest API view"""

    db = db
    model = None

    allowed_operators = (
        "$eq",
        "$not",
        "$null",
        "$in",
        "$gt",
        "$gte",
        "$lt",
        "$lte",
        "$btw",
    )
    sortable_fields = ("created_date", "updated_date")
    _default_filterable_fields = ("id",)

    def get(self, id: str = None) -> Response:
        """Get list of objects or one by object id

        Args:
            id (str, optional): object id. Defaults to None.

        Returns:
            Response: response object
        """
        if id:
            return self.model.query.get(id).to_dict()

        query = self.model.query

        # sort by
        try:
            query = self._apply_sort(query, request.args.get("sort"))
        except KeyError:
            pass

        # filters
        filters = []
        for key in request.args.keys():
            if key.startswith("filter."):
                column = key[len("filter.") :]
                value = request.args.get(key).split(":")
                filters.append((column, *value))

        query = self._apply_filters(query, filters)

        page = request.args.get("page") or 1
        limit = request.args.get("limit") or 10
        query = query.paginate(page=page, per_page=limit)

        return (
            {
                "data": [obj.to_dict() for obj in query.items],
                "meta": {"total": query.total, "page": page, "limit": limit},
            },
            status.HTTP_200_OK,
        )

    def post(self, obj=None, excludes=None) -> Response:
        data = request.json
        obj = obj or self.model()
        obj = self._update_obj(obj, data, update_id=True, excludes=excludes)

        self.db.session.add(obj)
        self.db.session.commit()

        return obj.to_dict(), status.HTTP_201_CREATED

    def patch(self, id: str = None, obj=None, excludes=None) -> Response:
        data = request.json

        if not obj:
            if not id:
                obj = self.model()
            else:
                obj = self.model.query.get(id)

        obj = self._update_obj(obj, data, excludes=excludes)

        self.db.session.add(obj)

        try:
            self.db.session.commit()
        except IntegrityError:
            return (
                {
                    "error": "Unexpected IntegrityError occurred when inserting into database."
                },
                status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return obj.to_dict()

    def delete(self, id: str = None) -> Response:
        if id is None:
            # TODO: Implement batch delete
            pass

        obj = self.model.query.get(id)
        self.db.session.delete(obj)
        self.db.session.commit()
        return obj.to_dict(), status.HTTP_200_OK

    def _update_obj(
        self, obj: Model, data: dict, update_id: bool = False, excludes: list = None
    ) -> Model:
        for k, v in data.items():
            if excludes:
                if k in excludes:
                    continue

            if hasattr(obj, k):
                if k == "id" and not update_id:
                    continue

                if isinstance(v, dict):
                    obj = self._update_obj(getattr(obj, k), v)
                    continue

                if isinstance(getattr(obj, k), InstrumentedList):
                    if isinstance(v, list):
                        self._update_obj_list(k, getattr(obj, k), v)
                    else:
                        raise Exception("Invalid input")
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

    def _update_obj_list(
        self, prop_name: str, obj_list: InstrumentedList, data_list: list
    ):
        """Update list of related objects from input data"""
        for data in data_list:
            updated = False
            if "id" in data:
                for obj in obj_list:
                    if str(obj.id) == data["id"]:
                        self._update_obj(obj, data)
                        updated = True
                        continue

            if not updated:
                # id not given or obj with this id not found
                model = getattr(self.model, prop_name).prop.entity.entity
                obj = model()
                obj_list.append(self._update_obj(obj, data))

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
    def _apply_sort(cls, query: Query, sort_args_str: str) -> Query:
        if not sort_args_str:
            return query

        column_name, *mode = map(lambda x: x.strip(), sort_args_str.split(","))
        mode = "".join(mode)

        if column_name not in cls.sortable_fields:
            return query

        column = getattr(cls.model, column_name)
        if mode in ["asc", "desc"]:
            column = getattr(column, mode)()

        return query.order_by(column)

    @classmethod
    def _apply_filters(cls, query: Query, filters: list) -> Query:
        """
        filter operators: $eq, $not, $null, $in, $gt, $gte, $lt, $lte, $btw
        """

        if len(filters) == 0:
            return query

        criterion = ()
        for curr_filter in filters:
            column_name, operator, value = (
                curr_filter if len(curr_filter) == 3 else (*curr_filter, None)
            )
            if column_name not in (
                *cls.filterable_fields,
                *cls._default_filterable_fields,
            ):
                continue
            if operator not in cls.allowed_operators:
                continue

            # TODO: Check if operation is allowed for column

            # TODO: store operator strings in object or enum
            if operator == "$eq":
                criterion += (getattr(cls.model, column_name) == value,)

        return query.filter(*criterion)

    @classmethod
    def register(
        cls,
        name: str,
        blueprint: Blueprint,
        pk="id",
        pk_type="string",
        methods=None,
        pk_methods=None,
    ):
        """Register view to flask app

        Args:
            name (str): resource name, set "" to use blueprint base path.
            blueprint (Blueprint): blueprint to register view to.
            pk (str, optional): name of primary key. Defaults to "id".
            pk_type (str, optional): type of primary key. Defaults to "string".
            methods (_type_, optional): methods at resource root. Defaults to None.
            pk_methods (_type_, optional): methods allowed with pk specified. Defaults to None.
        """

        view_func = cls.as_view(name)
        if methods is None or len(methods) > 0:
            blueprint.add_url_rule(
                view_func=view_func,
                rule=f"/{name}",
                methods=methods or ["GET", "POST", "PATCH"],
            )
        if pk_methods is None or len(pk_methods) > 0:
            blueprint.add_url_rule(
                view_func=view_func,
                rule=f"/{name}/<{pk_type}:{pk}>" if name else f"/<{pk_type}:{pk}>",
                methods=pk_methods or ["GET", "PATCH", "DELETE"],
            )
