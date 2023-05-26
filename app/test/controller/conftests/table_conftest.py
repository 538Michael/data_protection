import pytest


@pytest.fixture()
def base_table_post():
    table = {
        "name": "table name post",
    }

    return table


@pytest.fixture()
def base_table_put():
    table = {
        "name": "table name put",
    }

    return table
