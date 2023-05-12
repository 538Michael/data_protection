from app.main import db


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

    table = db.relationship("Table", back_populates="columns")

    def __repr__(self) -> str:
        return f"<Column {self.id}>"
