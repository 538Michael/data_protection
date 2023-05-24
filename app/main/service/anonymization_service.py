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
    # Get the table object with the specified ID, including the associated database information
    table = get_table(table_id=table_id, options=[joinedload(AnonTable.database)])

    try:
        # Create an engine based on the cloud URL of the table's database
        engine = create_engine(url=table.database.cloud_url)
    finally:
        # Check if the engine has the table, and if so, raise an exception
        if inspect(engine).has_table(table.name):
            raise DefaultException("table_already_anonymized", code=409)
        engine.dispose()

    # Clone the database by creating a destination table with the same structure and columns
    clone_database(
        database=table.database,
        src_table=table.name,
        dest_columns=[table.primary_key] + [column.name for column in table.columns],
    )

    # Create a new engine based on the URL of the table's database
    engine = create_engine(url=table.database.url)
    metadata = MetaData()

    # Get the primary key of the table
    primary_key = table.primary_key

    # Create a table object for the table, including the primary key and other columns
    tableObj = Table(
        table.name,
        metadata,
        include_columns=[primary_key] + [column.name for column in table.columns],
        extend_existing=True,
        autoload_with=engine,
    )

    # Create a dictionary mapping column names to column indexes for the table
    column_indexes = {
        column_name: index for index, column_name in enumerate(tableObj.columns.keys())
    }

    # Create a session for the engine
    session = Session(bind=engine)

    try:
        # Retrieve the results from the table in batches
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

                # Anonymize the values of each column in the row
                for column in table.columns:
                    # Seed the faker instance with a specific value based on the database, table, column, and row
                    faker.seed_instance(
                        f"database{table.database_id}table{table_id}column{column.name}row{row[0]}value{str(row[column_indexes[column.name]])}"
                    )
                    # Apply the anonymization mapping function for the column's anonymization type
                    values[column.name] = anonymization_mapping.get(
                        column.anonymization_type
                    )()
                rows_to_update.append(values)

            # Update the corresponding rows in the table using the anonymized values
            session.execute(
                tableObj.update().where(text(f"{primary_key} = :_{primary_key}")),
                rows_to_update,
            )
            session.commit()

            rows = results.fetchmany(batch_size)

    except Exception as e:
        print(e)

    finally:
        # Close the session
        session.close()

    # Dispose the engine
    engine.dispose()


def delete_anonymization(table_id: int):
    # Get the table object with the specified ID, including the associated database information
    table = get_table(table_id=table_id, options=[joinedload(AnonTable.database)])

    # Get the primary key of the table
    primary_key = table.primary_key

    try:
        # Create a source engine based on the cloud URL of the table's database
        src_engine = create_engine(url=table.database.cloud_url)
    except exc.OperationalError:
        raise DefaultException("cloud_database_not_exists", code=409)

    # Check if the source engine has the table
    if not inspect(src_engine).has_table(table.name):
        raise DefaultException("table_not_anonymized", code=409)

    # Create metadata and table objects for the source table
    src_metadata = MetaData()
    src_table = Table(
        table.name,
        src_metadata,
        autoload_with=src_engine,
    )

    # Create a session for the source engine
    src_session = Session(bind=src_engine)

    # Create a dictionary mapping column indices to column names for the source table
    column_names = {
        index: column_name for index, column_name in enumerate(src_table.columns.keys())
    }

    try:
        # Create a destination engine based on the URL of the table's database
        dest_engine = create_engine(url=table.database.url)
    except exc.OperationalError:
        raise DefaultException("database_not_exists", code=409)

    # Check if the destination engine has the table
    if not inspect(dest_engine).has_table(table.name):
        raise DefaultException("table_not_exists", code=409)

    # Create metadata and table objects for the destination table
    dest_metadata = MetaData()
    dest_table = Table(table.name, dest_metadata, autoload_with=src_engine)

    # Create a session for the destination engine
    dest_session = Session(bind=dest_engine)

    try:
        # Retrieve the results from the source table in batches
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

                # Iterate over the columns of the row and construct a dictionary of values
                for i, value in enumerate(row):
                    if i == 0:
                        values["_" + column_names[i]] = value
                    else:
                        values[column_names[i]] = value
                rows_to_update.append(values)

            # Update the corresponding rows in the destination table using the constructed values
            dest_session.execute(
                dest_table.update().where(text(f"{primary_key} = :_{primary_key}")),
                rows_to_update,
            )
            dest_session.commit()

            rows = results.fetchmany(batch_size)

    except exc.OperationalError:
        raise DefaultException("database_not_exists", code=409)
    except exc.NoSuchTableError:
        raise DefaultException("table_not_exists", code=409)
    except Exception as e:
        print(e)
    finally:
        # Close the source session
        src_session.close()

        # Drop the source table from the source engine
        src_table.drop(bind=src_engine, checkfirst=True)

        # Close the destination session
        dest_session.close()

        # Dispose the source and destination engines
        src_engine.dispose()
        dest_engine.dispose()


from app.main.service.database_service import clone_database
from app.main.service.table_service import get_table
