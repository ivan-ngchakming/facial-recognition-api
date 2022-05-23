import json
from flask.testing import FlaskClient


def test_photos_post(client: FlaskClient, app, db):

    input_url = "https://image.tmdb.org/t/p/original/wA1ZT3GSWvRjcJP96VRRARs9zEe.jpg"

    # TODO: create custom test client class
    res = client.post("/photos", json={"url": input_url})
    data = json.loads(res.data)

    assert data["url"] == input_url
