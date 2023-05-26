from datetime import datetime

import pytest

from app.main import db
from app.main.model import Table
from app.test.seeders import (
    create_base_seed_database,
    create_base_seed_table,
    create_base_seed_user,
)
from app.test.util import check_object_with_json


@pytest.fixture(scope="module")
def seeded_database(client, database):
    create_base_seed_user(db)
    create_base_seed_database(db)
    create_base_seed_table(db)


@pytest.mark.usefixtures("seeded_database")
class TestTableController:
    # --------------------- GET  ---------------------

    def test_get_tables_token_not_found(self, client, base_admin_auth):
        response = client.get("/table")

        assert response.json["message"] == "token_not_found"
        assert response.status_code == 404

    def test_get_tables(self, client, base_admin_auth):
        response = client.get(
            "/table", headers={"Authorization": f"Bearer {base_admin_auth}"}
        )

        assert response.status_code == 200
        assert len(response.json) == 4
        assert response.json["current_page"] == 1
        assert response.json["total_items"] == 4
        assert response.json["total_pages"] == 1
        for item in response.json["items"]:
            table = Table.query.filter(Table.id == item["id"]).one_or_none()
            check_object_with_json(object=table, json=item)

    def test_get_tables_user(self, client, base_auth):
        response = client.get(
            "/table", headers={"Authorization": f"Bearer {base_auth}"}
        )

        assert response.status_code == 200
        assert len(response.json) == 4
        assert response.json["current_page"] == 1
        assert response.json["total_items"] == 2
        assert response.json["total_pages"] == 1
        for item in response.json["items"]:
            table = Table.query.filter(Table.id == item["id"]).one_or_none()
            check_object_with_json(object=table, json=item)

    @pytest.mark.parametrize(
        "key, value, ids, total_items",
        [
            ("page", 1, range(1, 5), 4),
            ("page", 2, [], 4),
            ("per_page", 5, range(1, 5), 4),
            ("database_id", 1, [1, 2], 2),
            ("name", "1", [1], 1),
            ("name", "table name 1", [1], 1),
        ],
        ids=[
            "page",
            "empty_page",
            "per_page",
            "database_id",
            "complete_name",
            "incomplete_name",
        ],
    )
    def test_get_table_by_parameters(
        self, client, base_admin_auth, key, value, ids, total_items
    ):
        response = client.get(
            "/table",
            headers={"Authorization": f"Bearer {base_admin_auth}"},
            query_string={key: value},
        )

        assert len(response.json) == 4
        assert response.json["total_items"] == total_items
        assert len(response.json["items"]) == len(ids)
        for item in response.json["items"]:
            table = Table.query.filter(Table.id == item["id"]).one_or_none()
            check_object_with_json(object=table, json=item)

    # --------------------- GET BY ID ---------------------

    def test_get_table_token_not_found(self, client):
        response = client.get("/table/1")

        assert response.json["message"] == "token_not_found"
        assert response.status_code == 404

    def test_get_table(self, client, base_admin_auth):
        response = client.get(
            "/table/1", headers={"Authorization": f"Bearer {base_admin_auth}"}
        )

        assert response.status_code == 200
        assert len(response.json) == 4

        table = Table.query.filter(Table.id == 1).one_or_none()
        check_object_with_json(object=table, json=response.json)

    def test_get_table_that_not_exists(self, client, base_admin_auth):
        response = client.get(
            "/table/0", headers={"Authorization": f"Bearer {base_admin_auth}"}
        )

        assert response.json["message"] == "table_not_found"
        assert response.status_code == 404

    # --------------------- UPDATE ---------------------

    def test_update_table_token_not_found(self, client, base_table_put):
        response = client.put("/table/1", json=base_table_put)

        assert response.json["message"] == "token_not_found"
        assert response.status_code == 404

    @pytest.mark.parametrize(
        "key_popped",
        [
            "name",
        ],
        ids=[
            "name",
        ],
    )
    def test_update_table_without_required_data(
        self, client, base_admin_auth, base_table_put, key_popped
    ):
        base_table_put.pop(key_popped, None)
        response = client.put(
            "/table/1",
            headers={"Authorization": f"Bearer {base_admin_auth}"},
            json=base_table_put,
        )

        assert response.json["message"] == "Input payload validation failed"
        assert response.status_code == 400
        assert key_popped in response.json["errors"].keys()

    @pytest.mark.parametrize(
        "key, value",
        [
            ("name", 0),
            ("name", ""),
            ("name", "a" * 256),
        ],
        ids=[
            "invalid_name",
            "short_name",
            "long_name",
        ],
    )
    def test_update_table_with_invalid_data(
        self, client, base_admin_auth, base_table_put, key, value
    ):
        base_table_put[key] = value
        response = client.put(
            "/table/1",
            headers={"Authorization": f"Bearer {base_admin_auth}"},
            json=base_table_put,
        )

        assert response.json["message"] == "Input payload validation failed"
        assert response.status_code == 400
        assert key in response.json["errors"].keys()

    def test_update_table_that_not_exists(
        self, client, base_admin_auth, base_table_put
    ):
        response = client.put(
            "/table/0",
            headers={"Authorization": f"Bearer {base_admin_auth}"},
            json=base_table_put,
        )

        assert response.json["message"] == "table_not_found"
        assert response.status_code == 404

    def test_update_table_with_registered_data(
        self, client, base_admin_auth, base_table_put
    ):
        base_table_put["name"] = "table name 2"
        response = client.put(
            "/table/1",
            headers={"Authorization": f"Bearer {base_admin_auth}"},
            json=base_table_put,
        )

        assert response.json["message"] == "table_already_exist"
        assert response.status_code == 409

    def test_update_table(self, client, base_admin_auth, base_table_put):
        response = client.put(
            "/table/1",
            headers={"Authorization": f"Bearer {base_admin_auth}"},
            json=base_table_put,
        )

        assert response.json["message"] == "table_updated"
        assert response.status_code == 200

        table = Table.query.filter(Table.id == 1).one_or_none()

        check_object_with_json(object=table, json=base_table_put)

    # --------------------- POST ---------------------

    @pytest.mark.parametrize(
        "key_popped",
        [
            "name",
        ],
        ids=[
            "name",
        ],
    )
    def test_create_table_without_required_data(
        self, client, base_admin_auth, base_table_post, key_popped
    ):
        base_table_post.pop(key_popped, None)
        response = client.post(
            "/table/1",
            headers={"Authorization": f"Bearer {base_admin_auth}"},
            json=base_table_post,
        )

        assert response.json["message"] == "Input payload validation failed"
        assert response.status_code == 400
        assert key_popped in response.json["errors"].keys()

    @pytest.mark.parametrize(
        "key, value",
        [
            ("name", 0),
            ("name", ""),
            ("name", "a" * 256),
        ],
        ids=[
            "invalid_name",
            "short_name",
            "long_name",
        ],
    )
    def test_create_table_with_invalid_data(
        self, client, base_admin_auth, base_table_post, key, value
    ):
        base_table_post[key] = value
        response = client.post(
            "/table/1",
            headers={"Authorization": f"Bearer {base_admin_auth}"},
            json=base_table_post,
        )

        assert response.json["message"] == "Input payload validation failed"
        assert response.status_code == 400
        assert key in response.json["errors"].keys()

    def test_create_table_with_registered_data(
        self, client, base_admin_auth, base_table_post
    ):
        base_table_post["name"] = "table name 2"
        response = client.post(
            "/table/1",
            headers={"Authorization": f"Bearer {base_admin_auth}"},
            json=base_table_post,
        )

        assert response.json["message"] == "table_already_exist"
        assert response.status_code == 409

    def test_create_table(self, client, base_admin_auth, base_table_post):
        response = client.post(
            "/table/1",
            headers={"Authorization": f"Bearer {base_admin_auth}"},
            json=base_table_post,
        )

        assert response.json["message"] == "table_created"
        assert response.status_code == 201

        table = Table.query.order_by(Table.id.desc()).first()

        check_object_with_json(object=table, json=base_table_post)

        db.session.delete(table)
        db.session.commit()

    def test_create_table_user(self, client, base_auth, base_table_post):
        response = client.post(
            "/table/2",
            headers={"Authorization": f"Bearer {base_auth}"},
            json=base_table_post,
        )

        assert response.json["message"] == "table_created"
        assert response.status_code == 201

        table = Table.query.order_by(Table.id.desc()).first()

        check_object_with_json(object=table, json=base_table_post)

    # --------------------- DELETE ---------------------

    def test_delete_table_with_non_registered_id(self, client, base_admin_auth):
        response = client.delete(
            "/table/0", headers={"Authorization": f"Bearer {base_admin_auth}"}
        )

        assert response.json["message"] == "table_not_found"
        assert response.status_code == 404

    """def test_delete_table_associated_with_movimentation_item(
        self, client, base_admin_auth
    ):
        response = client.delete(
            "/table/1", headers={"Authorization": f"Bearer {base_admin_auth}"}
        )

        assert response.json["message"] == "table_associated_with_movimentation_item"
        assert response.status_code == 409"""

    def test_delete_table(self, client, base_admin_auth):
        response = client.delete(
            "/table/2",
            headers={"Authorization": f"Bearer {base_admin_auth}"},
        )

        assert response.json["message"] == "table_deleted"
        assert response.status_code == 200
