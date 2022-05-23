from server import create_app
import json


def test_config():
    assert not create_app().testing
    assert create_app({"TESTING": True}).testing


def test_index(client, app):
    res = client.get("/")
    data = json.loads(res.data)

    assert "version" in data
    assert data["version"] == app.config["ENV"]
