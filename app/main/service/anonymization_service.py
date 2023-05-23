import re

from sqlalchemy import MetaData, Table, create_engine, exc, inspect
from sqlalchemy.orm import joinedload
from sqlalchemy_utils import database_exists

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
}


def save_new_anonymization(table_id: int) -> None:
    # Get the table object with the specified ID, including the associated database
    table = get_table(table_id=table_id, options=[joinedload(AnonTable.database)])

    engine = create_engine(url=table.database.cloud_url)
    if inspect(engine).has_table(table.name):
        raise DefaultException("table_already_anonymized", code=409)
    engine.dispose()

    # Clone the database and create a new table with the same structure
    clone_database(
        database=table.database,
        src_table=table.name,
        dest_columns=[table.primary_key] + [column.name for column in table.columns],
    )

    try:
        # Create an engine to connect to the database and reflect existing columns
        engine = create_engine(url=table.database.url)
        metadata = MetaData()

        # Create a table object representing the old table structure
        tableObj = Table(
            table.name,
            metadata,
            include_columns=[table.primary_key]
            + [column.name for column in table.columns],
            extend_existing=True,
            autoload_with=engine,
        )

        # Begin a transaction with the database
        with engine.begin() as connection:
            # Select all rows from the old table
            results = connection.execute(tableObj.select())

            # Fetch the rows in batches of a specified size
            batch_size = 100000
            rows = results.fetchmany(batch_size)

            while rows:
                for row in rows:
                    values = {}
                    # Generate anonymized values for each column in the table
                    for column in table.columns:
                        faker.seed_instance(
                            f"database{table.database_id}table{table_id}column{column.name}row{row[0]}value{row[column.id]}"
                        )
                        values[column.name] = anonymization_mapping.get(
                            column.anonymization_type
                        )()

                    # Update the corresponding row in the new table with the anonymized values
                    connection.execute(
                        tableObj.update()
                        .where(tableObj.columns[table.primary_key] == row[0])
                        .values(values)
                    )

                # Fetch the next batch of rows
                rows = results.fetchmany(batch_size)
    except Exception as e:
        # Print any exceptions that occur during the process
        print(e)
    finally:
        # Close the database connection and dispose the engines
        connection.close()
        engine.dispose()


def delete_anonymization(table_id: int):
    # Get the table object with the specified ID, including the associated database
    table = get_table(table_id=table_id, options=[joinedload(AnonTable.database)])

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

    try:
        # Begin transactions with both source and destination databases
        with src_engine.begin() as src_connection, dest_engine.begin() as dest_connection:
            # Select all rows from the source table
            results = src_connection.execute(src_table.select())

            # Fetch the rows in batches of a specified size
            batch_size = 100000
            rows = results.fetchmany(batch_size)

            while rows:
                for row in rows:
                    # Update the corresponding row in the new table with the anonymized values
                    dest_connection.execute(
                        dest_table.update()
                        .where(dest_table.columns[table.primary_key] == row[0])
                        .values(tuple(row))
                    )

                # Fetch the next batch of rows
                rows = results.fetchmany(batch_size)

        src_table.drop(bind=src_engine, checkfirst=True)

    except exc.OperationalError:
        raise DefaultException("database_not_exists", code=409)
    except exc.NoSuchTableError:
        raise DefaultException("table_not_exists", code=409)
    except Exception as e:
        # Print any exceptions that occur during the process
        print(e)
    finally:
        # Close the connections and dispose of the engines
        src_connection.close()
        src_engine.dispose()
        dest_connection.close()
        dest_engine.dispose()


from app.main.service.database_service import clone_database
from app.main.service.table_service import get_table
