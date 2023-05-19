from app.main.model import Column


def add_columns(db):
    new_column = Column(table_id=1, name="name", anonymization_type="name")
    db.session.add(new_column)

    new_column = Column(table_id=1, name="data", anonymization_type="date")
    db.session.add(new_column)

    new_column = Column(table_id=1, name="cpf", anonymization_type="cpf")
    db.session.add(new_column)

    new_column = Column(table_id=1, name="rg", anonymization_type="rg")
    db.session.add(new_column)

    new_column = Column(table_id=1, name="ip", anonymization_type="ipv4")
    db.session.add(new_column)

    db.session.flush()
