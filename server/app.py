import importlib
from logging.config import dictConfig

import yaml
from flask_api import FlaskAPI
from flask_cors import CORS
from flask_migrate import Migrate

from .config import Config
from .database import db
from .theme import theme as theme_bp

# TODO: Disable file loggers in development environment
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


for name in ["core", "faces", "search", "scrapper", "profiles"]:
    try:
        importlib.import_module(f".{name}.models", "server")
    except ModuleNotFoundError:
        app.logger.debug(f"{name} does not have a models.py file")

    try:
        mod = importlib.import_module(f".{name}.views", "server")
    except ModuleNotFoundError:
        app.logger.debug(f"{name} does not have a views.py file")

    try:
        app.register_blueprint(mod.blueprint)
    except AttributeError:
        app.logger.debug(f"{name} does not have a blueprint.py file")


# override browsable api views
app.blueprints["flask-api"] = theme_bp


@app.shell_context_processor
def make_shell_context():
    return {"db": db}
