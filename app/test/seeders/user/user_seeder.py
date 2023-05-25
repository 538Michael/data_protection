from app.main.model import User
from app.main.service import hash_password


def create_base_seed_user(db):
    new_user = User(
        name="user@uece.br", password=hash_password("aaaaaaaa"), is_admin=True
    )

    db.session.add(new_user)

    new_user = User(name="user1@uece.br", password=hash_password("bbbbbbbb"))

    db.session.add(new_user)

    new_user = User(name="user2@uece.br", password=hash_password("cccccccc"))

    db.session.add(new_user)

    new_user = User(name="user3@uece.br", password=hash_password("dddddddd"))

    db.session.add(new_user)

    new_user = User(name="user4@uece.br", password=hash_password("eeeeeeee"))

    db.session.add(new_user)

    new_user = User(name="user5@uece.br", password=hash_password("ffffffff"))

    db.session.add(new_user)

    new_user = User(name="user6@uece.br", password=hash_password("gggggggg"))

    db.session.add(new_user)

    new_user = User(name="user7@uece.br", password=hash_password("hhhhhhhh"))

    db.session.add(new_user)

    new_user = User(name="user8@uece.br", password=hash_password("iiiiiiii"))

    db.session.add(new_user)

    db.session.commit()
