from app.main import db
from app.main.config import Config

DATABASE_TYPE = ["mysql", "postgresql"]


class Database(db.Model):
    __tablename__ = "database"
    _table_args_ = (
        db.UniqueConstraint(
            "type",
            "username",
            "host",
            "port",
            "name",
            name="unique_database_type_username_host_port_name",
        ),
    )

    id = db.Column(db.Integer, nullable=False, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    type = db.Column(db.Enum(*DATABASE_TYPE, name="database_type_enum"), nullable=False)
    username = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    host = db.Column(db.String(255), nullable=False)
    port = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(255), nullable=False)

    user = db.relationship("User", back_populates="databases")
    tables = db.relationship("Table", back_populates="database")

    @property
    def url(self) -> str:
        db_url = "{}://{}:{}@{}:{}/{}".format(
            self.type,
            self.username,
            self.password,
            self.host,
            self.port,
            self.name,
        )
        return db_url

    @property
    def cloud_url(self) -> str:
        cloud_db_url = "{}/{}".format(
            Config.CLOUD_URL[self.type],
            f"database{self.id}",
        )
        return cloud_db_url

    def __repr__(self) -> str:
        return f"<Database {self.id}>"
