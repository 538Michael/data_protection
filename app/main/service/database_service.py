import time
from math import ceil

from sqlalchemy import and_
from werkzeug.datastructures import ImmutableMultiDict

from app.main import db
from app.main.config import Config
from app.main.exceptions import DefaultException
from app.main.model import Database, User

_CONTENT_PER_PAGE = Config.DEFAULT_CONTENT_PER_PAGE


def get_databases(params: ImmutableMultiDict):
    page = params.get("page", type=int, default=1)
    per_page = params.get("per_page", type=int, default=_CONTENT_PER_PAGE)
    user_id = params.get("user_id", type=int)
    type = params.get("type", type=str)
    username = params.get("username", type=str)
    host = params.get("host", type=str)
    port = params.get("port", type=int)
    name = params.get("name", type=str)

    filters = []

    if user_id:
        filters.append(Database.user_id == user_id)
    if type:
        filters.append(Database.type == type)
    if username:
        filters.append(Database.username.ilike(f"%{username}%"))
    if host:
        filters.append(Database.host.ilike(f"%{host}%"))
    if port:
        filters.append(Database.port == port)
    if name:
        filters.append(Database.name.ilike(f"%{name}%"))

    pagination = (
        Database.query.filter(*filters)
        .order_by(Database.id)
        .paginate(page=page, per_page=per_page, error_out=False)
    )

    return {
        "current_page": page,
        "total_items": pagination.total,
        "total_pages": ceil(pagination.total / per_page),
        "items": pagination.items,
    }


def get_database_by_id(database_id: int) -> None:
    return get_database(database_id=database_id)


def save_new_database(data: dict[str, str]) -> None:
    type = data.get("type")
    username = data.get("username")
    host = data.get("host")
    port = data.get("port")
    name = data.get("name")

    user = get_user(user_id=data.get("user_id"))

    _validate_database_unique_constraint(
        type=type, username=username, host=host, port=port, name=name
    )

    new_database = Database(
        user=user,
        type=type,
        username=username,
        password=data.get("password"),
        host=host,
        port=port,
        name=name,
    )

    db.session.add(new_database)
    db.session.commit()


def update_database(database_id: int, data: dict[str, any]) -> None:
    new_type = data.get("type")
    new_username = data.get("username")
    new_host = data.get("host")
    new_port = data.get("port")
    new_name = data.get("name")

    database = get_database(database_id=database_id)

    _validate_database_unique_constraint(
        type=new_type,
        username=new_username,
        host=new_host,
        port=new_port,
        name=new_name,
        filters=[Database.id != database_id],
    )

    database.type = new_type
    database.username = new_username
    database.password = data.get("password")
    database.host = new_host
    database.port = new_port
    database.name = new_name

    db.session.commit()


def delete_database(database_id: int) -> None:
    database = get_database(database_id=database_id)

    db.session.delete(database)
    db.session.commit()


def get_database(database_id: int, options: list = None) -> Database:
    query = Database.query

    if options is not None:
        query = query.options(*options)

    database = query.filter(Database.id == database_id).one_or_none()

    if database is None:
        raise DefaultException("database_not_found", code=404)

    return database


def _validate_database_unique_constraint(
    type: str, username: str, host: str, port: int, name: str, filters: list = []
) -> None:
    if Database.query.filter(
        and_(
            Database.type == type,
            Database.username == username,
            Database.host == host,
            Database.port == port,
            Database.name == name,
        ),
        *filters,
    ).first():
        raise DefaultException("database_already_exist", code=409)


from app.main.service.user.user_service import get_user
