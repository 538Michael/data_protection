from app.main.model import Table
from app.main.service import hash_password


def create_base_seed_table(db):
    new_table = Table(
        database_id=1,
        name="table name 1",
    )

    db.session.add(new_table)

    new_table = Table(
        database_id=1,
        name="table name 2",
    )

    db.session.add(new_table)

    new_table = Table(
        database_id=2,
        name="table name 3",
    )

    db.session.add(new_table)

    new_table = Table(
        database_id=2,
        name="table name 4",
    )

    db.session.add(new_table)

    db.session.commit()
