from app.main import db


class Table(db.Model):
    __tablename__ = "table"
    _table_args_ = (
        db.UniqueConstraint(
            "database_id",
            "name",
            name="unique_table_database_id_name",
        ),
    )

    id = db.Column(db.Integer, nullable=False, autoincrement=True, primary_key=True)
    database_id = db.Column(
        db.Integer, db.ForeignKey("database.id"), nullable=False, unique=True
    )

    name = db.Column(db.String(255), nullable=False)

    database = db.relationship("Database", back_populates="tables")

    def __repr__(self) -> str:
        return f"<Table {self.id}>"
