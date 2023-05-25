from sqlalchemy import MetaData
from sqlalchemy import Table as saTable
from sqlalchemy import create_engine

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
    database_id = db.Column(db.Integer, db.ForeignKey("database.id"), nullable=False)

    name = db.Column(db.String(255), nullable=False)

    anonymized = db.Column(db.Boolean, nullable=False, server_default="false")

    database = db.relationship("Database", back_populates="tables")
    columns = db.relationship("Column", back_populates="table")

    def __repr__(self) -> str:
        return f"<Table {self.id}>"

    @property
    def primary_key(self):
        # create engine, reflect existing columns, and create table object for oldTable
        engine = create_engine(url=self.database.url)
        metadata = MetaData()
        tableObj = saTable(self.name, metadata, autoload_with=engine)
        primary_key = tableObj.primary_key.columns.keys()[0]
        engine.dispose()
        return primary_key
