import pytest

from app.main import db
from app.test.seeders import create_base_seed_user


@pytest.fixture(scope="module")
def seeded_database(client, database):
    """Seed database with user data"""

    return create_base_seed_user(db)


@pytest.mark.usefixtures("seeded_database")
class TestUserController:
    def test_get_users(self, client):
        response = client.get("/user")

        assert response.status_code == 200
        assert len(response.json) == 4
        assert response.json["current_page"] == 1
        assert response.json["total_items"] == 9
        assert response.json["total_pages"] == 1
        assert response.json["items"][0]["username"] == "user@uece.br"
        assert response.json["items"][1]["username"] == "user1@uece.br"
        assert response.json["items"][2]["username"] == "user2@uece.br"

    def test_get_users_by_page(self, client):
        response = client.get("/user", query_string={"page": 2})

        assert response.status_code == 200
        assert len(response.json) == 4
        assert len(response.json["items"]) == 0
        assert response.json["current_page"] == 2

    def test_get_user_by_id(self, client):
        response = client.get("/user/1")

        assert response.status_code == 200
        assert len(response.json) == 2
        assert response.json["id"] == 1
        assert response.json["username"] == "user@uece.br"

    def test_get_user_by_invalid_id(self, client):
        response = client.get("/user/999")

        assert response.status_code == 404
        assert response.json["message"] == "user_not_found"

    def test_update_user_with_invalid_id(self, client):
        response = client.patch("/user/0", json={"password": "new_password"})
        assert response.status_code == 404

    def test_register_user_with_registered_username(self, client, base_user):
        base_user["username"] = "user@uece.br"
        response = client.post("/user", json=base_user)
        assert response.status_code == 409
        assert response.json["message"] == "username_in_use"

    def test_register_user(self, client, base_user):
        response = client.post("/user", json=base_user)

        assert response.status_code == 201
        assert response.json["message"] == "user_created"
