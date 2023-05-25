import pytest


@pytest.fixture()
def base_database_post():
    database = {
        "user_id": 1,
        "type": "postgresql",
        "username": "database username post",
        "password": "database password post",
        "host": "database host post",
        "port": 1,
        "name": "database name post",
    }

    return database


@pytest.fixture()
def base_database_put():
    database = {
        "user_id": 1,
        "type": "postgresql",
        "username": "database username update",
        "password": "database password update",
        "host": "database host update",
        "port": 2,
        "name": "database name update",
    }

    return database
