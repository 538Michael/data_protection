import pytest


@pytest.fixture()
def base_user():
    """Base user data"""

    user = {"username": "new_user@uece.br", "password": "new_password"}

    return user
