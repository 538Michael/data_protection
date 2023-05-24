from app.main.model import Table


def add_tables(db):
    new_table = Table(database_id=1, name="user")
    db.session.add(new_table)

    new_table = Table(database_id=1, name="client_db_2")
    db.session.add(new_table)

    db.session.flush()
