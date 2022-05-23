import git
import platform
from flask import Blueprint, current_app


from . import controller

repo = git.Repo(search_parent_directories=True)


blueprint = Blueprint("core", __name__)


@blueprint.route("/")
def index():
    sha = repo.head.object.hexsha
    return {
        "version": current_app.config["ENV"],
        "sha": sha,
        "platform": platform.platform(),
    }


@blueprint.route("/memory")
def print_memory():
    return {"memory": controller.get_memory(), "unit": "mb"}
