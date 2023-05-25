import pytest

from app.main.service import create_jwt


@pytest.fixture()
def base_admin_auth():
    """Base admin auth data"""

    return create_jwt(user_id=1)


@pytest.fixture()
def base_auth():
    """Base auth data"""

    return create_jwt(user_id=2)
