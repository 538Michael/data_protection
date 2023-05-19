from app.main.model import Table


def add_tables(db):
    new_table = Table(database_id=1, name="user")
    db.session.add(new_table)

    db.session.flush()
