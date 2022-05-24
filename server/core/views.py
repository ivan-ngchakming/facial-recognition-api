import platform

import git
from flask import Blueprint, current_app

from .utils import get_memory

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
    return {"memory": get_memory(), "unit": "mb"}


@blueprint.route("/site-map")
def site_map():
    res = []
    for url in current_app.url_map.iter_rules():
        specs = {
            "endpoint": url.endpoint,
            "rule": url.rule,
            "methods": list(url.methods),
        }
        res.append(specs)

    return res
