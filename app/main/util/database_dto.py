from flask_restx import Namespace, fields

from app.main.model import DATABASE_TYPE


class DatabaseDTO:
    api = Namespace("database", description="database related operations")

    database_id = {"id": fields.Integer(description="database id")}

    database_user_id = {
        "user_id": fields.Integer(description="database user relationship", example=1)
    }

    database_type = {
        "type": fields.String(
            required=True,
            description="database type",
            enum=DATABASE_TYPE,
        )
    }

    database_username = {
        "username": fields.String(
            required=True, description="database username", min_length=1, max_length=255
        )
    }

    database_password = {
        "password": fields.String(
            required=True, description="database password", min_length=1, max_length=255
        )
    }

    database_host = {
        "host": fields.String(
            required=True, description="database host", min_length=1, max_length=255
        )
    }

    database_port = {
        "port": fields.Integer(required=True, description="database port", example=5432)
    }

    database_name = {
        "name": fields.String(
            required=True, description="database name", min_length=1, max_length=255
        )
    }

    database_post = api.model(
        "database_post",
        database_user_id
        | database_type
        | database_user_id
        | database_username
        | database_password
        | database_host
        | database_port
        | database_name,
    )

    database_update = api.clone("database_put", database_post)

    database_response = api.clone("database_response", database_id, database_post)

    database_list = api.model(
        "database_list",
        {
            "current_page": fields.Integer(),
            "total_items": fields.Integer(),
            "total_pages": fields.Integer(),
            "items": fields.List(fields.Nested(database_response)),
        },
    )
