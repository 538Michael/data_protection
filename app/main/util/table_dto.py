from flask_restx import Namespace, fields


class TableDTO:
    api = Namespace("table", description="table related operations")

    table_id = {"id": fields.Integer(description="table id")}

    table_database_id = {
        "database_id": fields.Integer(
            description="table database relationship", example=1
        )
    }

    table_name = {
        "name": fields.String(
            required=True, description="table name", min_length=1, max_length=255
        )
    }

    table_post = api.model("table_post", table_name)

    table_update = api.clone("table_put", table_post)

    table_response = api.clone(
        "table_response", table_id | table_database_id, table_post
    )

    table_list = api.model(
        "table_list",
        {
            "current_page": fields.Integer(),
            "total_items": fields.Integer(),
            "total_pages": fields.Integer(),
            "items": fields.List(fields.Nested(table_response)),
        },
    )
