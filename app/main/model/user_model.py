from app.main import db


class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(
        db.Boolean, nullable=False, default=False, server_default="false"
    )

    def __repr__(self) -> str:
        return f"<User {self.name}>"
