from math import ceil

from sqlalchemy import MetaData, Table, and_, create_engine, inspect
from sqlalchemy_utils import create_database, database_exists
from werkzeug.datastructures import ImmutableMultiDict

from app.main import db
from app.main.config import Config
from app.main.exceptions import DefaultException
from app.main.model import Database

_CONTENT_PER_PAGE = Config.DEFAULT_CONTENT_PER_PAGE


def get_databases(params: ImmutableMultiDict):
    page = params.get("page", type=int, default=1)
    per_page = params.get("per_page", type=int, default=_CONTENT_PER_PAGE)
    type = params.get("type", type=str)
    username = params.get("username", type=str)
    host = params.get("host", type=str)
    port = params.get("port", type=int)
    name = params.get("name", type=str)

    filters = []

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


def clone_database(database: Database, src_table: str, dest_columns: list = None):
    # Create an engine and metadata for the source database
    src_engine = create_engine(url=database.url)
    if not database_exists(url=src_engine.url):
        raise DefaultException("database_not_exists", code=409)

    if not inspect(src_engine).has_table(src_table):
        raise DefaultException("table_not_exists", code=409)

    src_metadata = MetaData()

    # Reflect the structure of the source table
    src_table = Table(
        src_table,
        src_metadata,
        include_columns=dest_columns,
        autoload_with=src_engine,
    )

    # Create an engine and metadata for the destination database
    dest_engine = create_engine(url=database.cloud_url)
    # Drop and recreate the destination table
    if not database_exists(url=dest_engine.url):
        create_database(url=dest_engine.url)

    dest_metadata = MetaData()

    # Create a table object representing the destination table
    dest_table = Table(
        src_table,
        dest_metadata,
        autoload_with=src_engine,
        include_columns=dest_columns,
    )

    dest_table.drop(bind=dest_engine, checkfirst=True)
    dest_table.create(bind=dest_engine, checkfirst=True)

    try:
        # Begin transactions with both source and destination databases
        with src_engine.begin() as src_connection, dest_engine.begin() as dest_connection:
            # Select all rows from the source table
            results = src_connection.execute(src_table.select())

            # Fetch the rows in batches of a specified size
            batch_size = 100000
            rows = results.fetchmany(batch_size)

            while rows:
                rows_values = [tuple(row) for row in rows]
                # Insert the rows into the destination table
                dest_connection.execute(dest_table.insert().values(rows_values))

                # Fetch the next batch of rows
                rows = results.fetchmany(batch_size)

    except Exception as e:
        # Print any exceptions that occur during the process
        print(e)
    finally:
        # Close the connections and dispose of the engines
        src_connection.close()
        src_engine.dispose()
        dest_connection.close()
        dest_engine.dispose()


from app.main.service.user.user_service import get_user
