import pytest

from app.main import db
from app.test.seeders import create_base_seed_user


@pytest.fixture(scope="module")
def seeded_database(client, database):
    """Seed database with user data"""

    return create_base_seed_user(db)


@pytest.mark.usefixtures("seeded_database")
class TestUserController:
    def test_get_users(self, client, base_admin_auth):
        response = client.get(
            "/user", headers={"Authorization": f"Bearer {base_admin_auth}"}
        )

        assert response.status_code == 200
        assert len(response.json) == 4
        assert response.json["current_page"] == 1
        assert response.json["total_items"] == 9
        assert response.json["total_pages"] == 1
        assert response.json["items"][0]["name"] == "user@uece.br"
        assert response.json["items"][1]["name"] == "user1@uece.br"
        assert response.json["items"][2]["name"] == "user2@uece.br"

    def test_get_users_by_page(self, client, base_admin_auth):
        response = client.get(
            "/user",
            headers={"Authorization": f"Bearer {base_admin_auth}"},
            query_string={"page": 2},
        )

        assert response.status_code == 200
        assert len(response.json) == 4
        assert len(response.json["items"]) == 0
        assert response.json["current_page"] == 2

    def test_get_user_by_id(self, client, base_auth):
        response = client.get(
            "/user/1", headers={"Authorization": f"Bearer {base_auth}"}
        )

        assert response.status_code == 200
        assert len(response.json) == 2
        assert response.json["id"] == 1
        assert response.json["name"] == "user@uece.br"

    def test_get_user_by_invalid_id(self, client, base_auth):
        response = client.get(
            "/user/0", headers={"Authorization": f"Bearer {base_auth}"}
        )

        assert response.status_code == 404
        assert response.json["message"] == "user_not_found"

    def test_register_user_with_registered_name(self, client, base_user):
        base_user["name"] = "user@uece.br"
        response = client.post("/user", json=base_user)
        assert response.status_code == 409
        assert response.json["message"] == "name_in_use"

    def test_register_user(self, client, base_user):
        response = client.post("/user", json=base_user)

        assert response.status_code == 201
        assert response.json["message"] == "user_created"
