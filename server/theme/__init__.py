from flask import Blueprint


theme = Blueprint(
    "flask-api",
    __name__,
    url_prefix="/flask-api",
    template_folder="templates",
    static_folder="static",
)
