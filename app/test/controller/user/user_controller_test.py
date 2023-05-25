import pytest

from app.main import db
from app.main.model import User
from app.test.seeders import create_base_seed_user
from app.test.util import check_object_with_json


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
        for item in response.json["items"]:
            user = User.query.filter(User.id == item["id"]).one_or_none()
            check_object_with_json(object=user, json=item)

    @pytest.mark.parametrize(
        "key, value, ids, total_items",
        [
            ("page", 1, range(1, 10), 9),
            ("page", 2, [], 9),
            ("per_page", 5, range(1, 6), 9),
            ("name", "user@uece.br", [1], 1),
            ("name", "user@uece", [1], 1),
        ],
        ids=[
            "page",
            "empty_page",
            "per_page",
            "complete_name",
            "incomplete_name",
        ],
    )
    def test_get_user_by_parameters(
        self, client, base_admin_auth, key, value, ids, total_items
    ):
        response = client.get(
            "/user",
            headers={"Authorization": f"Bearer {base_admin_auth}"},
            query_string={key: value},
        )

        assert len(response.json) == 4
        assert response.json["total_items"] == total_items
        assert len(response.json["items"]) == len(ids)
        for item in response.json["items"]:
            user = User.query.filter(User.id == item["id"]).one_or_none()
            check_object_with_json(object=user, json=item)

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
