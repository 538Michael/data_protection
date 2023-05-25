from datetime import datetime, timedelta
from functools import wraps
from typing import Dict

import jwt
from flask import request

from app.main.config import app_config
from app.main.exceptions import DefaultException
from app.main.model import User

_secret_key = app_config.SECRET_KEY
_jwt_exp = app_config.JWT_EXP


def login(data: Dict[str, any]) -> tuple[str, User]:
    user = User.query.filter_by(name=data.get("name")).first()

    if not user:
        raise DefaultException(message="password_incorrect_information", code=401)

    if not check_passwords(
        password=data.get("password"), hashed_password=user.password
    ):
        raise DefaultException("password_incorrect_information", code=401)

    return {
        "data": {
            "id": user.id,
            "name": user.name,
            "is_admin": user.is_admin,
            "token": create_jwt(user_id=user.id),
        }
    }


def jwt_required(admin_check: bool = False):
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            token = None

            if "Authorization" in request.headers:
                token = request.headers.get("Authorization")
                if not "Bearer " in token:
                    raise DefaultException("token_invalid", code=401)
                token = token.replace("Bearer ", "")

            if not token:
                raise DefaultException("token_not_found", code=404)

            try:
                data = jwt.decode(token, _secret_key, algorithms=["HS256"])
                current_user = User.query.filter(
                    User.id == data.get("id")
                ).one_or_none()
                if current_user is None:
                    raise DefaultException("user_not_found", code=404)
            except:
                raise DefaultException("token_invalid", code=401)

            if admin_check and not current_user.is_admin:
                raise DefaultException("administrator_privileges_required", code=403)

            return fn(current_user, *args, **kwargs)

        return decorator

    return wrapper


def create_jwt(user_id: int):
    return jwt.encode(
        {"id": user_id, "exp": datetime.utcnow() + timedelta(hours=_jwt_exp)},
        _secret_key,
    )


from app.main.service.user.password_service import check_passwords
