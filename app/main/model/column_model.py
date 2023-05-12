from app.main import db

ANONYMIZATION_TYPE = ["name", "date_time", "date", "time", "cpf", "rg", "ipv4", "ipv6"]


class Column(db.Model):
    __tablename__ = "column"
    _table_args_ = (
        db.UniqueConstraint(
            "table_id",
            "name",
            name="unique_column_table_id_name",
        ),
    )

    id = db.Column(db.Integer, nullable=False, autoincrement=True, primary_key=True)
    table_id = db.Column(db.Integer, db.ForeignKey("table.id"), nullable=False)

    name = db.Column(db.String(255), nullable=False)
    anonymization_type = db.Column(
        db.Enum(*ANONYMIZATION_TYPE, name="column_anonymization_type_enum"),
        nullable=False,
    )

    table = db.relationship("Table", back_populates="columns")

    def __repr__(self) -> str:
        return f"<Column {self.id}>"
