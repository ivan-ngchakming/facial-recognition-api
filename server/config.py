import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST") or "localhost"
DB_PORT = os.getenv("DB_PORT") or 5432
DB_NAME = os.getenv("DB_NAME") or "facial-recognition"
DB_USERNAME = os.getenv("DB_USERNAME") or "postgres"
DB_PASSWORD = os.getenv("DB_PASSWORD") or "postgres"


class Config:
    """
    Default flask configuration object
    """

    TESTING = False

    ENV = os.getenv("FLASK_ENV") or "development"

    SECRET_KEY = os.urandom(24)

    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    PROJECT_DIR = os.path.abspath(os.path.dirname(BASE_DIR))
    PUBLIC_DIR = f"{PROJECT_DIR}/public"

    SQLALCHEMY_DATABASE_URI = (
        f"postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MIGRATION_DIR = PROJECT_DIR + "/migrations"

    # File upload
    UPLOAD_FOLDER = f"{PROJECT_DIR}/public/static"
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

    INIT_TASK_WORKERS = 2


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}-test"
    )
