from app.main.model import User
from app.main.service import hash_password


def add_users(db):
    new_user = User(username="user@uece.br", password=hash_password("test1234"))
    db.session.add(new_user)

    db.session.flush()
