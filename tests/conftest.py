import pytest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from server import create_app
from server.config import TestingConfig
from server.database import db as _db


@pytest.fixture
def app() -> Flask:
    app = create_app(TestingConfig)

    with app.app_context():
        _db.create_all()

    yield app

    with app.app_context():
        _db.drop_all()


@pytest.fixture
def db() -> SQLAlchemy:
    return _db


@pytest.fixture
def app_empty_db(app):
    app = create_app(TestingConfig)
    with app.app_context():
        _db.session.remove()
        _db.drop_all()
        yield app
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def client(app: Flask):
    return app.test_client()


@pytest.fixture
def runner(app: Flask):
    return app.test_cli_runner()
