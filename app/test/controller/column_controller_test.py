from datetime import datetime

import pytest

from app.main import db
from app.main.model import Column
from app.test.seeders import (
    create_base_seed_column,
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
    create_base_seed_column(db)


@pytest.mark.usefixtures("seeded_database")
class TestColumnController:
    # --------------------- GET  ---------------------

    def test_get_columns_token_not_found(self, client, base_admin_auth):
        response = client.get("/column")

        assert response.json["message"] == "token_not_found"
        assert response.status_code == 404

    def test_get_columns(self, client, base_admin_auth):
        response = client.get(
            "/column", headers={"Authorization": f"Bearer {base_admin_auth}"}
        )

        assert response.status_code == 200
        assert len(response.json) == 4
        assert response.json["current_page"] == 1
        assert response.json["total_items"] == 4
        assert response.json["total_pages"] == 1
        for item in response.json["items"]:
            column = Column.query.filter(Column.id == item["id"]).one_or_none()
            check_object_with_json(object=column, json=item)

    def test_get_columns_user(self, client, base_auth):
        response = client.get(
            "/column", headers={"Authorization": f"Bearer {base_auth}"}
        )

        assert response.status_code == 200
        assert len(response.json) == 4
        assert response.json["current_page"] == 1
        assert response.json["total_items"] == 2
        assert response.json["total_pages"] == 1
        for item in response.json["items"]:
            column = Column.query.filter(Column.id == item["id"]).one_or_none()
            check_object_with_json(object=column, json=item)

    @pytest.mark.parametrize(
        "key, value, ids, total_items",
        [
            ("page", 1, range(1, 5), 4),
            ("page", 2, [], 4),
            ("per_page", 5, range(1, 5), 4),
            ("table_id", 1, [1, 2], 2),
            ("name", "1", [1], 1),
            ("name", "column name 1", [1], 1),
        ],
        ids=[
            "page",
            "empty_page",
            "per_page",
            "table_id",
            "complete_name",
            "incomplete_name",
        ],
    )
    def test_get_column_by_parameters(
        self, client, base_admin_auth, key, value, ids, total_items
    ):
        response = client.get(
            "/column",
            headers={"Authorization": f"Bearer {base_admin_auth}"},
            query_string={key: value},
        )

        assert len(response.json) == 4
        assert response.json["total_items"] == total_items
        assert len(response.json["items"]) == len(ids)
        for item in response.json["items"]:
            column = Column.query.filter(Column.id == item["id"]).one_or_none()
            check_object_with_json(object=column, json=item)

    # --------------------- GET BY ID ---------------------

    def test_get_column_token_not_found(self, client):
        response = client.get("/column/1")

        assert response.json["message"] == "token_not_found"
        assert response.status_code == 404

    def test_get_column(self, client, base_admin_auth):
        response = client.get(
            "/column/1", headers={"Authorization": f"Bearer {base_admin_auth}"}
        )

        assert response.status_code == 200
        assert len(response.json) == 4

        column = Column.query.filter(Column.id == 1).one_or_none()
        check_object_with_json(object=column, json=response.json)

    def test_get_column_that_not_exists(self, client, base_admin_auth):
        response = client.get(
            "/column/0", headers={"Authorization": f"Bearer {base_admin_auth}"}
        )

        assert response.json["message"] == "column_not_found"
        assert response.status_code == 404

    # --------------------- UPDATE ---------------------

    def test_update_column_token_not_found(self, client, base_column_put):
        response = client.put("/column/1", json=base_column_put)

        assert response.json["message"] == "token_not_found"
        assert response.status_code == 404

    @pytest.mark.parametrize(
        "key_popped",
        [
            "name",
            "anonymization_type",
        ],
        ids=[
            "name",
            "anonymization_type",
        ],
    )
    def test_update_column_without_required_data(
        self, client, base_admin_auth, base_column_put, key_popped
    ):
        base_column_put.pop(key_popped, None)
        response = client.put(
            "/column/1",
            headers={"Authorization": f"Bearer {base_admin_auth}"},
            json=base_column_put,
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
            ("anonymization_type", 0),
        ],
        ids=[
            "invalid_name",
            "short_name",
            "long_name",
            "invalid_anonymization_type",
        ],
    )
    def test_update_column_with_invalid_data(
        self, client, base_admin_auth, base_column_put, key, value
    ):
        base_column_put[key] = value
        response = client.put(
            "/column/1",
            headers={"Authorization": f"Bearer {base_admin_auth}"},
            json=base_column_put,
        )

        assert response.json["message"] == "Input payload validation failed"
        assert response.status_code == 400
        assert key in response.json["errors"].keys()

    def test_update_column_that_not_exists(
        self, client, base_admin_auth, base_column_put
    ):
        response = client.put(
            "/column/0",
            headers={"Authorization": f"Bearer {base_admin_auth}"},
            json=base_column_put,
        )

        assert response.json["message"] == "column_not_found"
        assert response.status_code == 404

    def test_update_column_with_registered_data(
        self, client, base_admin_auth, base_column_put
    ):
        base_column_put["name"] = "column name 2"
        response = client.put(
            "/column/1",
            headers={"Authorization": f"Bearer {base_admin_auth}"},
            json=base_column_put,
        )

        assert response.json["message"] == "column_already_exist"
        assert response.status_code == 409

    def test_update_column(self, client, base_admin_auth, base_column_put):
        response = client.put(
            "/column/1",
            headers={"Authorization": f"Bearer {base_admin_auth}"},
            json=base_column_put,
        )

        assert response.json["message"] == "column_updated"
        assert response.status_code == 200

        column = Column.query.filter(Column.id == 1).one_or_none()

        check_object_with_json(object=column, json=base_column_put)

    # --------------------- POST ---------------------

    @pytest.mark.parametrize(
        "key_popped",
        [
            "name",
            "anonymization_type",
        ],
        ids=[
            "name",
            "anonymization_type",
        ],
    )
    def test_create_column_without_required_data(
        self, client, base_admin_auth, base_column_post, key_popped
    ):
        base_column_post.pop(key_popped, None)
        response = client.post(
            "/column/1",
            headers={"Authorization": f"Bearer {base_admin_auth}"},
            json=base_column_post,
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
            ("anonymization_type", 0),
        ],
        ids=[
            "invalid_name",
            "short_name",
            "long_name",
            "invalid_anonymization_type",
        ],
    )
    def test_create_column_with_invalid_data(
        self, client, base_admin_auth, base_column_post, key, value
    ):
        base_column_post[key] = value
        response = client.post(
            "/column/1",
            headers={"Authorization": f"Bearer {base_admin_auth}"},
            json=base_column_post,
        )

        assert response.json["message"] == "Input payload validation failed"
        assert response.status_code == 400
        assert key in response.json["errors"].keys()

    def test_create_column_with_registered_data(
        self, client, base_admin_auth, base_column_post
    ):
        base_column_post["name"] = "column name 2"
        response = client.post(
            "/column/1",
            headers={"Authorization": f"Bearer {base_admin_auth}"},
            json=base_column_post,
        )

        assert response.json["message"] == "column_already_exist"
        assert response.status_code == 409

    def test_create_column(self, client, base_admin_auth, base_column_post):
        response = client.post(
            "/column/1",
            headers={"Authorization": f"Bearer {base_admin_auth}"},
            json=base_column_post,
        )

        assert response.json["message"] == "column_created"
        assert response.status_code == 201

        column = Column.query.order_by(Column.id.desc()).first()

        check_object_with_json(object=column, json=base_column_post)

        db.session.delete(column)
        db.session.commit()

    def test_create_column_user(self, client, base_auth, base_column_post):
        response = client.post(
            "/column/3",
            headers={"Authorization": f"Bearer {base_auth}"},
            json=base_column_post,
        )

        assert response.json["message"] == "column_created"
        assert response.status_code == 201

        column = Column.query.order_by(Column.id.desc()).first()

        check_object_with_json(object=column, json=base_column_post)

    # --------------------- DELETE ---------------------

    def test_delete_column_with_non_registered_id(self, client, base_admin_auth):
        response = client.delete(
            "/column/0", headers={"Authorization": f"Bearer {base_admin_auth}"}
        )

        assert response.json["message"] == "column_not_found"
        assert response.status_code == 404

    """def test_delete_column_associated_with_movimentation_item(
        self, client, base_admin_auth
    ):
        response = client.delete(
            "/column/1", headers={"Authorization": f"Bearer {base_admin_auth}"}
        )

        assert response.json["message"] == "column_associated_with_movimentation_item"
        assert response.status_code == 409"""

    def test_delete_column(self, client, base_admin_auth):
        response = client.delete(
            "/column/2",
            headers={"Authorization": f"Bearer {base_admin_auth}"},
        )

        assert response.json["message"] == "column_deleted"
        assert response.status_code == 200
