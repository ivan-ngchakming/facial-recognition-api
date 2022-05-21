import git
import platform
from flask import Blueprint, current_app, flash, request
from flask_api import status

from . import controller

repo = git.Repo(search_parent_directories=True)


blueprint = Blueprint("core", __name__)


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in current_app.config["ALLOWED_EXTENSIONS"]
    )


@blueprint.route("/")
def index():
    sha = repo.head.object.hexsha
    return {"version": "dev", "sha": sha, "platform": platform.platform()}


@blueprint.route("/memory")
def print_memory():
    return {"memory": controller.get_memory(), "unit": "mb"}


@blueprint.route("/upload", methods=["GET", "POST"])
def upload():
    """Upload an image file."""
    if request.method == "POST":
        # check if the post request has the file part
        if "file" not in request.files:
            flash("No file part")
            return "File not provided", status.HTTP_400_BAD_REQUEST

        file = request.files["file"]
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == "":
            flash("No selected file")
            return "File not selected", status.HTTP_400_BAD_REQUEST

        if file and allowed_file(file.filename):
            filename = controller.upload(file)
            return {"status": "success", "url": f"/public/{filename}"}

    if not current_app.debug:
        return "Access denied", status.HTTP_401_UNAUTHORIZED

    return {}
