from flask_restx import Namespace, fields


class UserDTO:
    api = Namespace("user", description="user related operations")

    user_post = api.model(
        "user_post",
        {
            "username": fields.String(
                required=True, description="user username", min_length=3, max_length=255
            ),
            "password": fields.String(
                required=True, description="user password", min_length=8, max_length=255
            ),
        },
    )

    user_put = api.model(
        "user_put",
        {
            "password": fields.String(
                required=True, description="user password", min_length=8, max_length=255
            )
        },
    )

    user_response = api.model(
        "user_response",
        {
            "id": fields.Integer(description="user id"),
            "username": fields.String(description="user username"),
        },
    )

    user_list = api.model(
        "user_list",
        {
            "current_page": fields.Integer(),
            "total_items": fields.Integer(),
            "total_pages": fields.Integer(),
            "items": fields.List(fields.Nested(user_response)),
        },
    )
