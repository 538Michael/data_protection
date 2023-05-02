from flask_restx import Namespace, fields


class UserDTO:
    api = Namespace("user", description="user related operations")

    user_id = {"id": fields.Integer(description="user id")}
    user_name = {
        "name": fields.String(
            required=True, description="user name", min_length=3, max_length=255
        )
    }
    user_password = {
        "password": fields.String(
            required=True, description="user password", min_length=8, max_length=255
        )
    }

    user_post = api.model("user_post", user_name | user_password)

    user_put = api.model("user_put", user_password)

    user_response = api.model(
        "user_response",
        user_id | user_name,
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
