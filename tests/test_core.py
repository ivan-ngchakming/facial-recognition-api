from server import create_app
import json

from server.config import TestingConfig


def test_config():
    assert not create_app().testing
    assert create_app(TestingConfig).testing


def test_index(client, app):
    res = client.get("/")
    data = json.loads(res.data)

    assert "version" in data
    assert data["version"] == app.config["ENV"]
