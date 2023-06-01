import os
import time
from math import ceil

from sqlalchemy import MetaData
from sqlalchemy import Table as saTable
from sqlalchemy import and_, create_engine, inspect
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session, joinedload
from sqlalchemy_utils import create_database, database_exists
from werkzeug.datastructures import ImmutableMultiDict

from app.main import db
from app.main.config import Config
from app.main.exceptions import DefaultException
from app.main.model import Database, Table, User

_CONTENT_PER_PAGE = Config.DEFAULT_CONTENT_PER_PAGE


def get_tables(current_user: User, params: ImmutableMultiDict):
    page = params.get("page", type=int, default=1)
    per_page = params.get("per_page", type=int, default=_CONTENT_PER_PAGE)
    database_id = params.get("database_id", type=int)
    name = params.get("name", type=str)

    filters = []

    if not current_user.is_admin:
        filters.append(Table.database.has(Database.user_id == current_user.id))
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


def get_table_by_id(current_user: User, table_id: int) -> None:
    table = get_table(table_id=table_id, options=[joinedload(Table.database)])

    verify_user(current_user=current_user, user_id=table.database.user_id)

    return table


def save_new_table(current_user: User, database_id: int, data: dict[str, str]) -> None:
    name = data.get("name")

    database = get_database(database_id=database_id)

    verify_user(current_user=current_user, user_id=database.user_id)

    _validate_table_unique_constraint(database_id=database_id, name=name)

    new_table = Table(database=database, name=name)

    db.session.add(new_table)
    db.session.commit()


def update_table(current_user: User, table_id: int, data: dict[str, any]) -> None:
    new_name = data.get("name")

    table = get_table(table_id=table_id, options=[joinedload(Table.database)])

    verify_user(current_user=current_user, user_id=table.database.user_id)

    _validate_table_unique_constraint(
        database_id=table.database_id,
        name=new_name,
        filters=[Table.id != table_id],
    )

    table.name = new_name

    db.session.commit()


def delete_table(current_user: User, table_id: int) -> None:
    table = get_table(table_id=table_id, options=[joinedload(Table.database)])

    verify_user(current_user=current_user, user_id=table.database.user_id)

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


def clone_table(table: Table, dest_columns: list = None):
    # Create an engine and metadata for the source database
    try:
        src_engine = create_engine(url=table.database.url)
    except OperationalError:
        raise DefaultException("database_not_exists", code=409)

    if not inspect(src_engine).has_table(table.name):
        raise DefaultException("table_not_exists", code=409)

    src_metadata = MetaData()

    # Reflect the structure of the source table
    src_table = saTable(
        table.name,
        src_metadata,
        include_columns=dest_columns,
        autoload_with=src_engine,
    )

    for column in table.columns:
        if not column.name in src_table.columns:
            raise DefaultException("column_not_exists", code=409)

    # Create a session for the source database
    src_session = Session(bind=src_engine)

    # Create an engine and metadata for the destination database
    try:
        create_database(url=table.database.cloud_url)
    except Exception:
        pass
    dest_engine = create_engine(url=table.database.cloud_url)

    dest_metadata = MetaData()

    # Create a table object representing the destination table
    dest_table = saTable(
        table.name,
        dest_metadata,
        autoload_with=src_engine,
        include_columns=dest_columns,
    )

    dest_table.drop(bind=dest_engine, checkfirst=True)
    dest_table.create(bind=dest_engine, checkfirst=True)

    # Create a session for the destination database
    dest_session = Session(bind=dest_engine)

    try:
        if not os.path.exists("data"):
            os.makedirs("data")

        if not os.path.exists("data/elapsed_time"):
            os.makedirs("data/elapsed_time")

        with open(f"data/elapsed_time/elapsed_time.txt", "a") as file:
            for i in range(10):
                print(i)
                # Select all rows from the source table
                results = src_session.execute(src_table.select())

                # Fetch the rows in batches of a specified size
                batch_size = 100000
                rows = results.fetchmany(batch_size)

                while rows:
                    start_time = time.time()
                    rows_values = [tuple(row) for row in rows]
                    # Insert the rows into the destination table
                    dest_session.execute(dest_table.insert().values(rows_values))

                    # Fetch the next batch of rows
                    rows = results.fetchmany(batch_size)

                    end_time = time.time()
                    elapsed_time = end_time - start_time

                    file.write(f"{elapsed_time}\n")

                dest_session.rollback()
            file.close()

    except Exception as e:
        dest_session.rollback()
        dest_session.close()
        dest_table.drop(bind=dest_engine, checkfirst=True)

        # Print any exceptions that occur during the process
        print(e)
    finally:
        # Close the session
        src_session.close()
        dest_session.close()
        # Dispose of the engines
        src_engine.dispose()
        dest_engine.dispose()

        dest_table.drop(bind=dest_engine, checkfirst=True)


from app.main.service.database_service import get_database
from app.main.service.user.user_service import verify_user
