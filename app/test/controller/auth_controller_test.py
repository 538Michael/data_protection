import jwt
import pytest

from app.main import db
from app.main.config import app_config
from app.main.service import create_jwt
from app.test.seeders import create_base_seed_user

_secret_key = app_config.SECRET_KEY


@pytest.fixture(scope="module")
def seeded_database(client, database):
    """Seed database with user data"""

    return create_base_seed_user(db)


@pytest.mark.usefixtures("seeded_database")
class TestLoginController:
    def test_user_login_with_wrong_password(self, client):
        response = client.post(
            "/user/auth",
            json={"name": "user@uece.br", "password": "12345678"},
        )

        assert response.status_code == 401
        assert response.json["message"] == "password_incorrect_information"

    def test_user_login_with_invalid_login(self, client):
        response = client.post(
            "/user/auth", json={"name": "user", "password": "12345678"}
        )

        assert response.status_code == 401
        assert response.json["message"] == "password_incorrect_information"

    def test_user_login(self, client):
        response = client.post(
            "/user/auth", json={"name": "user@uece.br", "password": "aaaaaaaa"}
        )

        assert response.status_code == 200
        assert len(response.json) == 1
        assert len(response.json["data"]) == 4
        response.json["data"]["id"] = 1
        response.json["data"]["name"] = "user@uece.br"
        response.json["data"]["is_admin"] = 0

    def test_jwt_required_without_token(self, client, base_admin_auth):
        response = client.get("/user")

        assert response.json["message"] == "token_not_found"
        assert response.status_code == 404

    @pytest.mark.parametrize(
        "token",
        ["Bearer invalid_token", "invalid_token"],
        ids=["invalid_bearer_token", "invalid_token"],
    )
    def test_jwt_required_with_invalid_token(self, client, token):
        response = client.get("/user", headers={"Authorization": f"{token}"})

        assert response.json["message"] == "token_invalid"
        assert response.status_code == 401

    def test_jwt_required_with_expired_token(self, client):
        token = jwt.encode(
            {"exp": 0},
            _secret_key,
        )
        response = client.get("/user", headers={"Authorization": f"Bearer {token}"})

        assert response.json["message"] == "token_invalid"
        assert response.status_code == 401

    def test_jwt_required_with_invalid_user(self, client):
        token = create_jwt(user_id=0)
        response = client.get("/user", headers={"Authorization": f"Bearer {token}"})

        assert response.json["message"] == "token_invalid"
        assert response.status_code == 401

    def test_jwt_required_with_not_admin_user(self, client, base_auth):
        response = client.get("/user", headers={"Authorization": f"Bearer {base_auth}"})

        assert response.json["message"] == "administrator_privileges_required"
        assert response.status_code == 403

    def test_jwt_required_with_valid_token(self, client, base_admin_auth):
        response = client.get(
            "/user", headers={"Authorization": f"Bearer {base_admin_auth}"}
        )

        assert response.status_code == 200
