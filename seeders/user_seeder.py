from app.main.model import User
from app.main.service import hash_password


def add_users(db):
    new_user = User(
        name="user@uece.br", password=hash_password("test1234"), is_admin=True
    )
    db.session.add(new_user)

    db.session.flush()
