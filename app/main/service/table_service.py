from math import ceil

from sqlalchemy import and_
from werkzeug.datastructures import ImmutableMultiDict

from app.main import db
from app.main.config import Config
from app.main.exceptions import DefaultException
from app.main.model import Table

_CONTENT_PER_PAGE = Config.DEFAULT_CONTENT_PER_PAGE


def get_tables(params: ImmutableMultiDict):
    page = params.get("page", type=int, default=1)
    per_page = params.get("per_page", type=int, default=_CONTENT_PER_PAGE)
    database_id = params.get("database_id", type=int)
    name = params.get("name", type=str)

    filters = []

    if database_id:
        filters.append(Table.database_id == database_id)
    if name:
        filters.append(Table.name.ilike(f"%{name}%"))

    pagination = (
        Table.query.filter(*filters)
        .order_by(Table.id)
        .paginate(page=page, per_page=per_page, error_out=False)
    )

    return {
        "current_page": page,
        "total_items": pagination.total,
        "total_pages": ceil(pagination.total / per_page),
        "items": pagination.items,
    }


def get_table_by_id(table_id: int) -> None:
    return get_table(table_id=table_id)


def save_new_table(database_id: int, data: dict[str, str]) -> None:
    name = data.get("name")

    database = get_database(database_id=database_id)

    _validate_table_unique_constraint(database_id=database_id, name=name)

    new_table = Table(database=database, name=name)

    db.session.add(new_table)
    db.session.commit()


def update_table(table_id: int, data: dict[str, any]) -> None:
    new_name = data.get("name")

    table = get_table(table_id=table_id)

    _validate_table_unique_constraint(
        database=table.database_id,
        name=new_name,
        filters=[Table.id != table_id],
    )

    table.name = new_name

    db.session.commit()


def delete_table(table_id: int) -> None:
    table = get_table(table_id=table_id)

    db.session.delete(table)
    db.session.commit()


def get_table(table_id: int, options: list = None) -> Table:
    query = Table.query

    if options is not None:
        query = query.options(*options)

    table = query.filter(Table.id == table_id).one_or_none()

    if table is None:
        raise DefaultException("table_not_found", code=404)

    return table


def _validate_table_unique_constraint(
    database_id: str, name: str, filters: list = []
) -> None:
    if Table.query.filter(
        and_(
            Table.database_id == database_id,
            Table.name == name,
        ),
        *filters,
    ).first():
        raise DefaultException("table_already_exist", code=409)


from app.main.service.database_service import get_database
