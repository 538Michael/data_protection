from flask_restx import Namespace, fields

from app.main.util.user.user_dto import UserDTO

_user_name = UserDTO.user_name
_user_password = UserDTO.user_password


class AuthDTO:
    api = Namespace("auth", description="Authentication related operations")

    auth_login = api.model("auth_login", _user_name | _user_password)

    auth_response = api.model(
        "auth_response",
        {
            "data": fields.Nested(
                api.model(
                    "auth_response_data",
                    {
                        "id": fields.Integer(description="user id"),
                        "name": fields.String(description="user name"),
                        "is_admin": fields.Integer(description="user admin flag"),
                        "token": fields.String(description="user token"),
                    },
                )
            ),
        },
    )
