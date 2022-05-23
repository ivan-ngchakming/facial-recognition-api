import importlib
from logging.config import dictConfig

import yaml
from ariadne import graphql_sync
from ariadne.constants import PLAYGROUND_HTML
from flask import jsonify, request
from flask_api import FlaskAPI
from flask_cors import CORS
from flask_migrate import Migrate

from .config import Config
from .database import db
from .faces.models import *  # noqa
from .legacy.schema import schema
from .theme import theme as theme_bp

dictConfig(yaml.load(open(Config.PROJECT_DIR + "/logging.yaml"), yaml.FullLoader))


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


# Setup database
db.init_app(app)

# Setup migration
migrate = Migrate(app, db, directory=app.config["MIGRATION_DIR"])


for name in ["core", "faces", "search", "scrapper"]:
    mod = importlib.import_module(f".{name}.views", "server")
    app.register_blueprint(mod.blueprint)


# override browsable api views
app.blueprints["flask-api"] = theme_bp


# TODO: remove
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


@app.shell_context_processor
def make_shell_context():
    return {"db": db}
