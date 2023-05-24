import re
import time

from sqlalchemy import MetaData, Table, create_engine, exc, inspect, text
from sqlalchemy.orm import Session, joinedload

from app.main import faker
from app.main.exceptions import DefaultException
from app.main.model import Table as AnonTable


def fix_cpf(cpf: str):
    if cpf is None:
        return None

    cpf = re.sub("[.-]", "", cpf)
    return cpf


def fix_rg(rg: str):
    if rg is None:
        return None

    return rg.replace("X", "0")


anonymization_mapping = {
    "name": faker.name,
    "address": faker.address,
    "email": faker.ascii_email,
    "date_time": faker.date_time,
    "date": faker.date,
    "time": faker.time,
    "cpf": lambda: fix_cpf(faker.cpf()),
    "rg": lambda: fix_rg(faker.rg()),
    "ipv4": faker.ipv4,
    "ipv6": faker.ipv6,
    "phone_number": faker.phone_number,
    "cellphone_number": faker.cellphone_number,
}


def save_new_anonymization(table_id: int) -> None:
    # Get the table object with the specified ID, including the associated database
    table = get_table(table_id=table_id, options=[joinedload(AnonTable.database)])

    try:
        engine = create_engine(url=table.database.cloud_url)
    finally:
        if inspect(engine).has_table(table.name):
            raise DefaultException("table_already_anonymized", code=409)
        engine.dispose()

    # Clone the database and create a new table with the same structure
    clone_database(
        database=table.database,
        src_table=table.name,
        dest_columns=[table.primary_key] + [column.name for column in table.columns],
    )

    # Create an engine to connect to the database and reflect existing columns
    engine = create_engine(url=table.database.url)
    metadata = MetaData()

    primary_key = table.primary_key

    # Create a table object representing the old table structure
    tableObj = Table(
        table.name,
        metadata,
        include_columns=[primary_key] + [column.name for column in table.columns],
        extend_existing=True,
        autoload_with=engine,
    )

    column_indexes = {
        column_name: index for index, column_name in enumerate(tableObj.columns.keys())
    }

    # Create a session
    session = Session(bind=engine)

    try:
        # Select all rows from the old table
        results = session.execute(
            tableObj.select().order_by(tableObj.columns[table.primary_key])
        )

        # Fetch the rows in batches of a specified size
        batch_size = 100000
        rows = results.fetchmany(batch_size)

        while rows:
            rows_to_update = []
            for row in rows:
                values = {}
                values["_" + primary_key] = row[0]
                # Generate anonymized values for each column in the table
                for column in table.columns:
                    faker.seed_instance(
                        f"database{table.database_id}table{table_id}column{column.name}row{row[0]}value{str(row[column_indexes[column.name]])}"
                    )
                    values[column.name] = anonymization_mapping.get(
                        column.anonymization_type
                    )()
                rows_to_update.append(values)

            # Update the corresponding rows in the new table with the anonymized values
            session.execute(
                tableObj.update().where(text(f"{primary_key} = :_{primary_key}")),
                rows_to_update,
            )
            session.commit()

            # Fetch the next batch of rows
            rows = results.fetchmany(batch_size)

    except Exception as e:
        # Print any exceptions that occur during the process
        print(e)

    finally:
        # Close the session
        session.close()

    # Dispose the engine
    engine.dispose()


def delete_anonymization(table_id: int):
    # Get the table object with the specified ID, including the associated database
    table = get_table(table_id=table_id, options=[joinedload(AnonTable.database)])

    primary_key = table.primary_key

    # Create an engine and metadata for the source database
    try:
        src_engine = create_engine(url=table.database.cloud_url)
    except exc.OperationalError:
        raise DefaultException("cloud_database_not_exists", code=409)

    if not inspect(src_engine).has_table(table.name):
        raise DefaultException("table_not_anonymized", code=409)

    src_metadata = MetaData()

    # Reflect the structure of the source table
    src_table = Table(
        table.name,
        src_metadata,
        autoload_with=src_engine,
    )

    # Create a session
    src_session = Session(bind=src_engine)

    column_names = {
        index: column_name for index, column_name in enumerate(src_table.columns.keys())
    }

    # Create an engine and metadata for the destination database
    try:
        dest_engine = create_engine(url=table.database.url)
    except exc.OperationalError:
        raise DefaultException("database_not_exists", code=409)

    if not inspect(dest_engine).has_table(table.name):
        raise DefaultException("table_not_exists", code=409)

    dest_metadata = MetaData()

    # Create a table object representing the destination table
    dest_table = Table(table.name, dest_metadata, autoload_with=src_engine)

    # Create a session
    dest_session = Session(bind=dest_engine)

    try:
        # Select all rows from the source table
        results = src_session.execute(
            src_table.select().order_by(src_table.columns[table.primary_key])
        )

        # Fetch the rows in batches of a specified size
        batch_size = 100000
        rows = results.fetchmany(batch_size)

        while rows:
            rows_to_update = []
            for row in rows:
                values = {}
                # Prepare the values for the update statement
                for i, value in enumerate(row):
                    if i == 0:
                        values["_" + column_names[i]] = value
                    else:
                        values[column_names[i]] = value
                rows_to_update.append(values)

            # Update the corresponding rows in the new table with the anonymized values
            dest_session.execute(
                dest_table.update().where(text(f"{primary_key} = :_{primary_key}")),
                rows_to_update,
            )
            dest_session.commit()

            # Fetch the next batch of rows
            rows = results.fetchmany(batch_size)

    except exc.OperationalError:
        raise DefaultException("database_not_exists", code=409)
    except exc.NoSuchTableError:
        raise DefaultException("table_not_exists", code=409)
    except Exception as e:
        # Print any exceptions that occur during the process
        print(e)
    finally:
        # Close the session
        src_session.close()

        src_table.drop(bind=src_engine, checkfirst=True)

        dest_session.close()
        # Dispose of the engines
        src_engine.dispose()
        dest_engine.dispose()


from app.main.service.database_service import clone_database
from app.main.service.table_service import get_table
