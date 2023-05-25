import pytest

from app.main import db
from app.test.seeders import create_base_seed_user


@pytest.fixture(scope="module")
def seeded_database(client, database):
    """Seed database with user data"""

    return create_base_seed_user(db)


@pytest.mark.usefixtures("seeded_database")
class TestPasswordController:
    # ---------------- Change password when logged in ----------------

    def test_change_password_with_distinct_passwords(self, client, base_auth):
        response = client.patch(
            "/user/password/change/1",
            headers={"Authorization": f"Bearer {base_auth}"},
            json={
                "current_password": "bbbbbbbb",
                "new_password": "123456789",
                "repeat_new_password": "987654321",
            },
        )

        assert response.status_code == 409
        assert response.json["message"] == "passwords_not_match"

    def test_change_password_with_invalid_user(self, client, base_auth):
        response = client.patch(
            "/user/password/change/0",
            headers={"Authorization": f"Bearer {base_auth}"},
            json={
                "current_password": "aaaaaaaaa",
                "new_password": "123456789",
                "repeat_new_password": "123456789",
            },
        )

        assert response.status_code == 404
        assert response.json["message"] == "user_not_found"

    def test_change_password(self, client, base_auth):
        response = client.patch(
            "/user/password/change/1",
            headers={"Authorization": f"Bearer {base_auth}"},
            json={
                "current_password": "aaaaaaaa",
                "new_password": "123456789",
                "repeat_new_password": "123456789",
            },
        )

        assert response.status_code == 200
        assert response.json["message"] == "password_updated"
