from math import ceil

from werkzeug.datastructures import ImmutableMultiDict

from app.main import db
from app.main.config import Config
from app.main.exceptions import DefaultException
from app.main.model import User

_CONTENT_PER_PAGE = Config.DEFAULT_CONTENT_PER_PAGE


def get_users(params: ImmutableMultiDict):
    page = params.get("page", type=int, default=1)
    per_page = params.get("per_page", type=int, default=_CONTENT_PER_PAGE)
    name = params.get("name", type=str)

    filters = []

    if name:
        filters.append(User.name.ilike(f"%{name}%"))

    pagination = (
        User.query.filter(*filters)
        .order_by(User.id)
        .paginate(page=page, per_page=per_page, error_out=False)
    )

    return {
        "current_page": page,
        "total_items": pagination.total,
        "total_pages": ceil(pagination.total / per_page),
        "items": pagination.items,
    }


def get_user_by_id(user_id: int) -> None:
    return get_user(user_id=user_id)


def save_new_user(data: dict[str, str]) -> None:
    user = User.query.filter_by(name=data.get("name")).scalar()

    if user:
        raise DefaultException("name_in_use", code=409)

    new_user = User(name=data.get("name"), password=hash_password(data.get("password")))

    db.session.add(new_user)
    db.session.commit()


def get_user(user_id: int, options: list = None) -> User:
    query = User.query

    if options is not None:
        query = query.options(*options)

    user = query.filter(User.id == user_id).one_or_none()

    if user is None:
        raise DefaultException("user_not_found", code=404)

    return user


def verify_user(current_user: User, user_id: int):
    if (not current_user.is_admin) and (user_id != current_user.id):
        raise DefaultException("user_unauthorized", code=401)


from app.main.service.user.password_service import hash_password
