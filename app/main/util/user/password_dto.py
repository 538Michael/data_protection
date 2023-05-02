from flask_restx import Namespace, fields


class PasswordDTO:
    api = Namespace("password", description="password related operations")

    password_current = {
        "current_password": fields.String(
            required=True, description="current user password", min_length=8
        )
    }
    password_new = {
        "new_password": fields.String(
            required=True, description="new user password", min_length=8
        )
    }
    password_new_repeat = {
        "repeat_new_password": fields.String(
            required=True, description="repeat new user password", min_length=8
        )
    }

    password_change = api.model(
        "password_change", password_current | password_new | password_new_repeat
    )
