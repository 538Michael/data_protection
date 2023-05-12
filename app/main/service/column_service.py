from math import ceil

from sqlalchemy import and_
from werkzeug.datastructures import ImmutableMultiDict

from app.main import db
from app.main.config import Config
from app.main.exceptions import DefaultException
from app.main.model import Column

_CONTENT_PER_PAGE = Config.DEFAULT_CONTENT_PER_PAGE


def get_columns(params: ImmutableMultiDict):
    page = params.get("page", type=int, default=1)
    per_page = params.get("per_page", type=int, default=_CONTENT_PER_PAGE)
    table_id = params.get("table_id", type=int)
    name = params.get("name", type=str)

    filters = []

    if table_id:
        filters.append(Column.table_id == table_id)
    if name:
        filters.append(Column.name.ilike(f"%{name}%"))

    pagination = (
        Column.query.filter(*filters)
        .order_by(Column.id)
        .paginate(page=page, per_page=per_page, error_out=False)
    )

    return {
        "current_page": page,
        "total_items": pagination.total,
        "total_pages": ceil(pagination.total / per_page),
        "items": pagination.items,
    }


def get_column_by_id(column_id: int) -> None:
    return get_column(column_id=column_id)


def save_new_column(table_id: int, data: dict[str, str]) -> None:
    name = data.get("name")

    table = get_table(table_id=table_id)

    _validate_column_unique_constraint(table_id=table_id, name=name)

    new_column = Column(
        table=table,
        name=name,
    )

    db.session.add(new_column)
    db.session.commit()


def update_column(column_id: int, data: dict[str, any]) -> None:
    new_name = data.get("name")

    column = get_column(column_id=column_id)

    _validate_column_unique_constraint(
        database=column.table_id,
        name=new_name,
        filters=[Column.id != column_id],
    )

    column.name = new_name

    db.session.commit()


def delete_column(column_id: int) -> None:
    column = get_column(column_id=column_id)

    db.session.delete(column)
    db.session.commit()


def get_column(column_id: int, options: list = None) -> Column:
    query = Column.query

    if options is not None:
        query = query.options(*options)

    column = query.filter(Column.id == column_id).one_or_none()

    if column is None:
        raise DefaultException("column_not_found", code=404)

    return column


def _validate_column_unique_constraint(
    table_id: str, name: str, filters: list = []
) -> None:
    if Column.query.filter(
        and_(
            Column.table_id == table_id,
            Column.name == name,
        ),
        *filters,
    ).first():
        raise DefaultException("column_already_exist", code=409)


from app.main.service.table_service import get_table
