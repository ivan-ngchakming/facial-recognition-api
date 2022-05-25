import errno
import importlib
import os
from logging.config import dictConfig

import yaml
from flask_api import FlaskAPI
from flask_cors import CORS
from flask_migrate import Migrate
from werkzeug.middleware.shared_data import SharedDataMiddleware

from server.middlewares import CORSMiddleware

from .config import Config
from .database import db
from .theme import theme as theme_bp

allowed_origins = [
    "http://localhost:3000",
    "http://localhost:5000",
    "https://facial-recognition.ivan0313.tk",
    "https://facial-recognition-api.ivan0313.tk",
    "https://facesearch.ivan0313.tk",
]


def create_app(config=Config) -> FlaskAPI:
    # logging configurations
    loggingConfig = yaml.load(
        open(Config.PROJECT_DIR + "/logging.yaml"), yaml.FullLoader
    )

    if config.ENV != "production":
        to_remove = []
        for key in loggingConfig["handlers"]:
            if key.endswith("_file"):
                to_remove.append(key)
        for key in to_remove:
            loggingConfig["handlers"].pop(key)
        loggingConfig["root"]["handlers"].remove("info_file")
        loggingConfig["root"]["handlers"].remove("error_file")
    else:
        try:
            os.makedirs("logs")
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

    dictConfig(loggingConfig)

    app = FlaskAPI(__name__)
    app.config.from_object(config)

    app.wsgi_app = SharedDataMiddleware(
        app.wsgi_app,
        {"/static": os.path.join(Config.PUBLIC_DIR, "static")},
        cache=True,
        cache_timeout=60 * 60 * 24 * 30,  # 31 days
    )

    app.wsgi_app = SharedDataMiddleware(
        app.wsgi_app,
        {"/models": os.path.join(Config.PUBLIC_DIR, "models")},
        cache=True,
        cache_timeout=60 * 60 * 24 * 30 * 12,  # 12 months
    )

    app.wsgi_app = CORSMiddleware(app.wsgi_app, allowed_origins, ["/models", "/static"])

    CORS(app, origins=allowed_origins)

    # Setup database
    db.init_app(app)

    # Setup migration
    Migrate(app, db, directory=app.config["MIGRATION_DIR"])

    for name in ["core", "faces", "photos", "profiles", "scrapper"]:
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

    return app
