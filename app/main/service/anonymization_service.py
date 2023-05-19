import re

from sqlalchemy import MetaData, Table, create_engine
from sqlalchemy.orm import joinedload

from app.main import faker
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

    # Clone the database and create a new table with the same structure
    clone_database(
        database=table.database,
        src_table=table.name,
        dest_columns=[table.primary_key] + [column.name for column in table.columns],
    )

    # Create an engine to connect to the database and reflect existing columns
    engine = create_engine(url=table.database.url)
    metadata = MetaData()

    # Create a table object representing the old table structure
    tableObj = Table(
        table.name,
        metadata,
        include_columns=[table.primary_key] + [column.name for column in table.columns],
        extend_existing=True,
        autoload_with=engine,
    )

    try:
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
                            f"database{table.database_id}table{table_id}column{column.name}row{row[0]}value{row[column.name]}"
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


from app.main.service.database_service import clone_database
from app.main.service.table_service import get_table
