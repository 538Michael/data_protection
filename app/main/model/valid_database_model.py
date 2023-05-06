from app.main import db


class ValidDatabase(db.Model):
    __tablename__ = "valid_database"

    id = db.Column(db.Integer, nullable=False, autoincrement=True, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)

    databases = db.relationship("Database", back_populates="valid_database")

    def __repr__(self):
        return f"<ValidDatabase {self.name}>"
