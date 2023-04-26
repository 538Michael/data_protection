from flask import current_app


def test_app(client):
    assert current_app is not None
    assert current_app.config["TESTING"] == True
    assert client is not None
