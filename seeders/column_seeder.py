from app.main.model import Column


def add_columns(db):
    new_column = Column(table_id=1, name="name", anonymization_type="name")
    db.session.add(new_column)

    new_column = Column(table_id=1, name="address", anonymization_type="address")
    db.session.add(new_column)

    new_column = Column(table_id=1, name="email", anonymization_type="email")
    db.session.add(new_column)

    new_column = Column(table_id=1, name="data", anonymization_type="date")
    db.session.add(new_column)

    new_column = Column(table_id=1, name="cpf", anonymization_type="cpf")
    db.session.add(new_column)

    new_column = Column(table_id=1, name="rg", anonymization_type="rg")
    db.session.add(new_column)

    new_column = Column(table_id=1, name="ip", anonymization_type="ipv4")
    db.session.add(new_column)

    new_column = Column(
        table_id=1, name="phone_number", anonymization_type="phone_number"
    )
    db.session.add(new_column)

    new_column = Column(
        table_id=1, name="cellphone_number", anonymization_type="cellphone_number"
    )
    db.session.add(new_column)

    new_column = Column(table_id=2, name="nome", anonymization_type="name")
    db.session.add(new_column)

    new_column = Column(table_id=2, name="endereco", anonymization_type="address")
    db.session.add(new_column)

    new_column = Column(table_id=2, name="email", anonymization_type="email")
    db.session.add(new_column)

    new_column = Column(table_id=2, name="data_hora", anonymization_type="date_time")
    db.session.add(new_column)

    new_column = Column(table_id=2, name="data", anonymization_type="date")
    db.session.add(new_column)

    new_column = Column(table_id=2, name="time", anonymization_type="time")
    db.session.add(new_column)

    new_column = Column(table_id=2, name="cpf", anonymization_type="cpf")
    db.session.add(new_column)

    new_column = Column(table_id=2, name="rg", anonymization_type="rg")
    db.session.add(new_column)

    new_column = Column(table_id=2, name="ipv4", anonymization_type="ipv4")
    db.session.add(new_column)

    new_column = Column(table_id=2, name="ipv6", anonymization_type="ipv6")
    db.session.add(new_column)

    new_column = Column(table_id=2, name="telefone", anonymization_type="phone_number")
    db.session.add(new_column)

    new_column = Column(
        table_id=2, name="celular", anonymization_type="cellphone_number"
    )
    db.session.add(new_column)

    new_column = Column(table_id=3, name="name", anonymization_type="name")
    db.session.add(new_column)

    new_column = Column(table_id=3, name="data", anonymization_type="date")
    db.session.add(new_column)

    new_column = Column(table_id=3, name="cpf", anonymization_type="cpf")
    db.session.add(new_column)

    new_column = Column(table_id=3, name="rg", anonymization_type="rg")
    db.session.add(new_column)

    new_column = Column(table_id=3, name="ip", anonymization_type="ipv4")
    db.session.add(new_column)

    new_column = Column(table_id=4, name="name", anonymization_type="name")
    db.session.add(new_column)

    new_column = Column(table_id=4, name="data", anonymization_type="date")
    db.session.add(new_column)

    new_column = Column(table_id=4, name="cpf", anonymization_type="cpf")
    db.session.add(new_column)

    new_column = Column(table_id=4, name="rg", anonymization_type="rg")
    db.session.add(new_column)

    new_column = Column(table_id=4, name="ip", anonymization_type="ipv4")
    db.session.add(new_column)

    db.session.flush()
