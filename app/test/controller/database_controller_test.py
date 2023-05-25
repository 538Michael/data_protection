from datetime import datetime

import pytest

from app.main import db
from app.main.model import Database
from app.test.seeders import create_base_seed_database, create_base_seed_user
from app.test.util import check_object_with_json


@pytest.fixture(scope="module")
def seeded_database(client, database):
    create_base_seed_user(db)
    create_base_seed_database(db)


@pytest.mark.usefixtures("seeded_database")
class TestDatabaseController:
    # --------------------- GET  ---------------------

    def test_get_databases_token_not_found(self, client, base_admin_auth):
        response = client.get("/database")

        assert response.json["message"] == "token_not_found"
        assert response.status_code == 404

    def test_get_databases(self, client, base_admin_auth):
        response = client.get(
            "/database", headers={"Authorization": f"Bearer {base_admin_auth}"}
        )

        assert response.status_code == 200
        assert len(response.json) == 4
        assert response.json["current_page"] == 1
        assert response.json["total_items"] == 2
        assert response.json["total_pages"] == 1
        for item in response.json["items"]:
            database = Database.query.filter(Database.id == item["id"]).one_or_none()
            check_object_with_json(object=database, json=item)

    def test_get_databases_user(self, client, base_auth):
        response = client.get(
            "/database", headers={"Authorization": f"Bearer {base_auth}"}
        )

        assert response.status_code == 200
        assert len(response.json) == 4
        assert response.json["current_page"] == 1
        assert response.json["total_items"] == 1
        assert response.json["total_pages"] == 1
        for item in response.json["items"]:
            database = Database.query.filter(Database.id == item["id"]).one_or_none()
            check_object_with_json(object=database, json=item)

    @pytest.mark.parametrize(
        "key, value, ids, total_items",
        [
            ("page", 1, [1, 2], 2),
            ("page", 2, [], 2),
            ("per_page", 5, [1, 2], 2),
            ("user_id", 1, [1], 1),
            ("type", "postgresql", [1], 1),
            ("username", "1", [1], 1),
            ("username", "database username 1", [1], 1),
            ("host", "1", [1], 1),
            ("host", "database host 1", [1], 1),
            ("port", 1, [1], 1),
            ("name", "1", [1], 1),
            ("name", "database name 1", [1], 1),
        ],
        ids=[
            "page",
            "empty_page",
            "per_page",
            "user_id",
            "type",
            "complete_username",
            "incomplete_username",
            "complete_host",
            "incomplete_host",
            "port",
            "complete_name",
            "incomplete_name",
        ],
    )
    def test_get_database_by_parameters(
        self, client, base_admin_auth, key, value, ids, total_items
    ):
        response = client.get(
            "/database",
            headers={"Authorization": f"Bearer {base_admin_auth}"},
            query_string={key: value},
        )

        assert len(response.json) == 4
        assert response.json["total_items"] == total_items
        assert len(response.json["items"]) == len(ids)
        for item in response.json["items"]:
            database = Database.query.filter(Database.id == item["id"]).one_or_none()
            check_object_with_json(object=database, json=item)

    # --------------------- GET BY ID ---------------------

    def test_get_database_token_not_found(self, client):
        response = client.get("/database/1")

        assert response.json["message"] == "token_not_found"
        assert response.status_code == 404

    def test_get_database(self, client, base_admin_auth):
        response = client.get(
            "/database/1", headers={"Authorization": f"Bearer {base_admin_auth}"}
        )

        assert response.status_code == 200
        assert len(response.json) == 8

        database = Database.query.filter(Database.id == 1).one_or_none()
        check_object_with_json(object=database, json=response.json)

    def test_get_database_that_not_exists(self, client, base_admin_auth):
        response = client.get(
            "/database/0", headers={"Authorization": f"Bearer {base_admin_auth}"}
        )

        assert response.json["message"] == "database_not_found"
        assert response.status_code == 404

    # --------------------- UPDATE ---------------------

    def test_update_database_token_not_found(self, client, base_database_put):
        response = client.put("/database/1", json=base_database_put)

        assert response.json["message"] == "token_not_found"
        assert response.status_code == 404

    @pytest.mark.parametrize(
        "key_popped",
        [
            "type",
            "username",
            "password",
            "host",
            "port",
            "name",
        ],
        ids=[
            "type",
            "username",
            "password",
            "host",
            "port",
            "name",
        ],
    )
    def test_update_database_without_required_data(
        self, client, base_admin_auth, base_database_put, key_popped
    ):
        base_database_put.pop(key_popped, None)
        response = client.put(
            "/database/1",
            headers={"Authorization": f"Bearer {base_admin_auth}"},
            json=base_database_put,
        )

        assert response.json["message"] == "Input payload validation failed"
        assert response.status_code == 400
        assert key_popped in response.json["errors"].keys()

    @pytest.mark.parametrize(
        "key, value",
        [
            ("type", "invalid_type"),
            ("username", 0),
            ("username", ""),
            ("username", "a" * 256),
            ("password", 0),
            ("password", ""),
            ("password", "a" * 256),
            ("host", 0),
            ("host", ""),
            ("host", "a" * 256),
            ("port", ""),
            ("name", 0),
            ("name", ""),
            ("name", "a" * 256),
        ],
        ids=[
            "invalid_type",
            "invalid_username",
            "short_username",
            "long_username",
            "invalid_password",
            "short_password",
            "long_password",
            "invalid_host",
            "short_host",
            "long_host",
            "port",
            "invalid_name",
            "short_name",
            "long_name",
        ],
    )
    def test_update_database_with_invalid_data(
        self, client, base_admin_auth, base_database_put, key, value
    ):
        base_database_put[key] = value
        response = client.put(
            "/database/1",
            headers={"Authorization": f"Bearer {base_admin_auth}"},
            json=base_database_put,
        )

        assert response.json["message"] == "Input payload validation failed"
        assert response.status_code == 400
        assert key in response.json["errors"].keys()

    def test_update_database_that_not_exists(
        self, client, base_admin_auth, base_database_put
    ):
        response = client.put(
            "/database/0",
            headers={"Authorization": f"Bearer {base_admin_auth}"},
            json=base_database_put,
        )

        assert response.json["message"] == "database_not_found"
        assert response.status_code == 404

    def test_update_database_with_registered_data(
        self, client, base_admin_auth, base_database_put
    ):
        base_database_put["type"] = "mysql"
        base_database_put["username"] = "database username 2"
        base_database_put["password"] = "database password 2"
        base_database_put["host"] = "database host 2"
        base_database_put["port"] = 2
        base_database_put["name"] = "database name 2"
        response = client.put(
            "/database/1",
            headers={"Authorization": f"Bearer {base_admin_auth}"},
            json=base_database_put,
        )

        assert response.json["message"] == "database_already_exist"
        assert response.status_code == 409

    def test_update_database(self, client, base_admin_auth, base_database_put):
        response = client.put(
            "/database/1",
            headers={"Authorization": f"Bearer {base_admin_auth}"},
            json=base_database_put,
        )

        assert response.json["message"] == "database_updated"
        assert response.status_code == 200

        database = Database.query.filter(Database.id == 1).one_or_none()

        check_object_with_json(object=database, json=base_database_put)

    # --------------------- POST ---------------------

    @pytest.mark.parametrize(
        "key_popped",
        [
            "type",
            "username",
            "password",
            "host",
            "port",
            "name",
        ],
        ids=[
            "type",
            "username",
            "password",
            "host",
            "port",
            "name",
        ],
    )
    def test_create_database_without_required_data(
        self, client, base_admin_auth, base_database_post, key_popped
    ):
        base_database_post.pop(key_popped, None)
        response = client.post(
            "/database",
            headers={"Authorization": f"Bearer {base_admin_auth}"},
            json=base_database_post,
        )

        assert response.json["message"] == "Input payload validation failed"
        assert response.status_code == 400
        assert key_popped in response.json["errors"].keys()

    @pytest.mark.parametrize(
        "key, value",
        [
            ("type", "invalid_type"),
            ("username", 0),
            ("username", ""),
            ("username", "a" * 256),
            ("password", 0),
            ("password", ""),
            ("password", "a" * 256),
            ("host", 0),
            ("host", ""),
            ("host", "a" * 256),
            ("port", ""),
            ("name", 0),
            ("name", ""),
            ("name", "a" * 256),
        ],
        ids=[
            "invalid_type",
            "invalid_username",
            "short_username",
            "long_username",
            "invalid_password",
            "short_password",
            "long_password",
            "invalid_host",
            "short_host",
            "long_host",
            "port",
            "invalid_name",
            "short_name",
            "long_name",
        ],
    )
    def test_create_database_with_invalid_data(
        self, client, base_admin_auth, base_database_post, key, value
    ):
        base_database_post[key] = value
        response = client.post(
            "/database",
            headers={"Authorization": f"Bearer {base_admin_auth}"},
            json=base_database_post,
        )

        assert response.json["message"] == "Input payload validation failed"
        assert response.status_code == 400
        assert key in response.json["errors"].keys()

    def test_create_database_with_registered_data(
        self, client, base_admin_auth, base_database_post
    ):
        base_database_post["type"] = "mysql"
        base_database_post["username"] = "database username 2"
        base_database_post["password"] = "database password 2"
        base_database_post["host"] = "database host 2"
        base_database_post["port"] = 2
        base_database_post["name"] = "database name 2"
        response = client.post(
            "/database",
            headers={"Authorization": f"Bearer {base_admin_auth}"},
            json=base_database_post,
        )

        assert response.json["message"] == "database_already_exist"
        assert response.status_code == 409

    def test_create_database(self, client, base_admin_auth, base_database_post):
        response = client.post(
            "/database",
            headers={"Authorization": f"Bearer {base_admin_auth}"},
            json=base_database_post,
        )

        assert response.json["message"] == "database_created"
        assert response.status_code == 201

        database = Database.query.order_by(Database.id.desc()).first()

        check_object_with_json(object=database, json=base_database_post)

        db.session.delete(database)
        db.session.commit()

    def test_create_database_user(self, client, base_auth, base_database_post):
        base_database_post["user_id"] = 2
        response = client.post(
            "/database",
            headers={"Authorization": f"Bearer {base_auth}"},
            json=base_database_post,
        )

        assert response.json["message"] == "database_created"
        assert response.status_code == 201

        database = Database.query.order_by(Database.id.desc()).first()

        check_object_with_json(object=database, json=base_database_post)

    # --------------------- DELETE ---------------------

    def test_delete_database_with_non_registered_id(self, client, base_admin_auth):
        response = client.delete(
            "/database/0", headers={"Authorization": f"Bearer {base_admin_auth}"}
        )

        assert response.json["message"] == "database_not_found"
        assert response.status_code == 404

    """def test_delete_database_associated_with_movimentation_item(
        self, client, base_admin_auth
    ):
        response = client.delete(
            "/database/1", headers={"Authorization": f"Bearer {base_admin_auth}"}
        )

        assert response.json["message"] == "database_associated_with_movimentation_item"
        assert response.status_code == 409"""

    def test_delete_database(self, client, base_admin_auth):
        response = client.delete(
            "/database/2",
            headers={"Authorization": f"Bearer {base_admin_auth}"},
        )

        assert response.json["message"] == "database_deleted"
        assert response.status_code == 200
