from app.main.model import Database


def add_databases(db):
    new_database = Database(
        user_id=1,
        type="postgresql",
        username="postgres",
        password="postgres",
        host="localhost",
        port=5432,
        name="test_database",
    )
    db.session.add(new_database)

    new_database = Database(
        user_id=1,
        type="postgresql",
        username="michaelsouza",
        password="larces132*",
        host="client-database.postgres.uhserver.com",
        port=5432,
        name="client_database",
    )
    db.session.add(new_database)

    db.session.flush()
