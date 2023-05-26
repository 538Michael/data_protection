from app.main.model import Column
from app.main.service import hash_password


def create_base_seed_column(db):
    new_column = Column(
        table_id=1,
        name="column name 1",
        anonymization_type="name",
    )

    db.session.add(new_column)

    new_column = Column(
        table_id=1,
        name="column name 2",
        anonymization_type="address",
    )

    db.session.add(new_column)

    new_column = Column(
        table_id=3,
        name="column name 3",
        anonymization_type="email",
    )

    db.session.add(new_column)

    new_column = Column(
        table_id=3,
        name="column name 4",
        anonymization_type="cpf",
    )

    db.session.add(new_column)

    db.session.commit()
