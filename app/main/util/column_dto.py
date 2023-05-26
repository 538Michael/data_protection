from flask_restx import Namespace, fields

from app.main.model import ANONYMIZATION_TYPE


class ColumnDTO:
    api = Namespace("column", description="column related operations")

    column_id = {"id": fields.Integer(description="column id")}

    column_table_id = {
        "table_id": fields.Integer(
            description="column database relationship", example=1
        )
    }

    column_name = {
        "name": fields.String(
            required=True, description="column name", min_length=1, max_length=255
        )
    }
    column_anonymization_type = {
        "anonymization_type": fields.String(
            required=True,
            description="column anonymization_type",
            enum=ANONYMIZATION_TYPE,
        )
    }

    column_post = api.model("column_post", column_name | column_anonymization_type)

    column_update = api.clone("column_put", column_post)

    column_response = api.clone(
        "column_response", column_id | column_table_id, column_post
    )

    column_list = api.model(
        "column_list",
        {
            "current_page": fields.Integer(),
            "total_items": fields.Integer(),
            "total_pages": fields.Integer(),
            "items": fields.List(fields.Nested(column_response)),
        },
    )
