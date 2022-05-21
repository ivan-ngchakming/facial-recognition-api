import importlib
import logging

from ariadne import graphql_sync
from ariadne.constants import PLAYGROUND_HTML
from flask import jsonify, request
from flask_api import FlaskAPI
from flask_cors import CORS
from flask_migrate import Migrate

from .config import Config
from .database import db
from .faces.models import *  # noqa
from .legacy.commands import build_cli, data_cli, dev_cli
from .legacy.schema import schema
from .legacy.taskmanager import manager as task_manager
from .logging_utils import get_console_handler
from .theme import theme as theme_bp

app = FlaskAPI(
    __name__, static_folder=f"{Config.PROJECT_DIR}/public", static_url_path="/"
)
CORS(
    app,
    origins=[
        "http://localhost:3000",
        "http://localhost:5000",
        "https://facial-recognition.ivan0313.tk",
        "https://facial-recognition-api.ivan0313.tk",
        "https://facesearch.ivan0313.tk",
    ],
)
app.config.from_object(Config)


# Create loggers and handlers
werkzeug_logger = logging.getLogger("werkzeug")  # grabs underlying WSGI logger
werkzeug_logger.setLevel(logging.INFO)
werkzeug_logger.addHandler(get_console_handler())

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(get_console_handler())

app.logger.setLevel(logging.DEBUG)

# Setup database
db.init_app(app)

# Setup migration
migrate = Migrate(app, db, directory=app.config["MIGRATION_DIR"])

# Setup task manager
task_manager.init_app(app)


for name in [".core.views", ".faces.views"]:
    mod = importlib.import_module(name, __name__)
    app.register_blueprint(mod.blueprint)


# override browsable api views
app.blueprints["flask-api"] = theme_bp


@app.route("/graphql", methods=["GET", "POST"])
def graphql():
    if request.method == "GET":
        return PLAYGROUND_HTML, 200
    else:
        # GraphQL queries are always sent as POST
        data = request.get_json()

        # Note: Passing the request to the context is optional.
        # In Flask, the current request is always accessible as flask.request
        success, result = graphql_sync(
            schema, data, context_value=request, debug=app.debug
        )

        status_code = 200 if success else 400
        return jsonify(result), status_code


# Register CLI Groups
app.cli.add_command(build_cli)
app.cli.add_command(data_cli)
app.cli.add_command(dev_cli)


@app.shell_context_processor
def make_shell_context():
    return {"db": db}
