from bcrypt import checkpw, gensalt, hashpw

from app.main import db
from app.main.exceptions import DefaultException


def change_password(data: dict[str, str], user_id: int) -> None:
    user = get_user(user_id=user_id)

    new_password = data.get("new_password")
    repeat_new_password = data.get("repeat_new_password")

    if not new_password == repeat_new_password:
        raise DefaultException("passwords_not_match", code=409)

    if not check_passwords(
        password=data.get("current_password"), hashed_password=user.password
    ):
        raise DefaultException("password_incorrect_information", code=409)

    user.password = hash_password(password=new_password)

    db.session.commit()


def hash_password(password: str) -> str:
    return hashpw(password=password.encode("utf-8"), salt=gensalt()).decode("utf-8")


def check_passwords(password: str, hashed_password: str) -> bool:
    return checkpw(
        password=password.encode("utf-8"),
        hashed_password=hashed_password.encode("utf-8"),
    )


from app.main.service.user.user_service import get_user
