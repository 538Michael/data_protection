import pytest


@pytest.fixture()
def base_column_post():
    column = {
        "name": "column name post",
        "anonymization_type": "name",
    }

    return column


@pytest.fixture()
def base_column_put():
    column = {
        "name": "column name put",
        "anonymization_type": "address",
    }

    return column
