import git
import platform
from flask import Blueprint


from . import controller

repo = git.Repo(search_parent_directories=True)


blueprint = Blueprint("core", __name__)


@blueprint.route("/")
def index():
    sha = repo.head.object.hexsha
    return {"version": "dev", "sha": sha, "platform": platform.platform()}


@blueprint.route("/memory")
def print_memory():
    return {"memory": controller.get_memory(), "unit": "mb"}
