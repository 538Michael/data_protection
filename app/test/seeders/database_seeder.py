from app.main.model import Database
from app.main.service import hash_password


def create_base_seed_database(db):
    new_database = Database(
        user_id=1,
        type="postgresql",
        username="database username 1",
        password="database password 1",
        host="database host 1",
        port=1,
        name="database name 1",
    )

    db.session.add(new_database)

    new_database = Database(
        user_id=2,
        type="mysql",
        username="database username 2",
        password="database password 2",
        host="database host 2",
        port=2,
        name="database name 2",
    )

    db.session.add(new_database)

    db.session.commit()
