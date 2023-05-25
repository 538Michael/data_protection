from flask import request
from flask_restx import Resource

from app.main.config import Config
from app.main.service import (
    delete_table,
    get_table_by_id,
    get_tables,
    jwt_required,
    save_new_table,
    update_table,
)
from app.main.util import DefaultResponsesDTO, TableDTO

table_ns = TableDTO.api
api = table_ns
_table_post = TableDTO.table_post
_table_update = TableDTO.table_update
_table_response = TableDTO.table_response
_table_list = TableDTO.table_list

_default_message_response = DefaultResponsesDTO.message_response
_validation_error_response = DefaultResponsesDTO.validation_error

_CONTENT_PER_PAGE = Config.CONTENT_PER_PAGE
_DEFAULT_CONTENT_PER_PAGE = Config.DEFAULT_CONTENT_PER_PAGE


@api.route("")
class Table(Resource):
    @api.doc(
        "List tables with pagination",
        params={
            "page": {"description": "Page number", "default": 1, "type": int},
            "per_page": {
                "description": "Items per page",
                "default": _DEFAULT_CONTENT_PER_PAGE,
                "enum": _CONTENT_PER_PAGE,
                "type": int,
            },
            "database_id": {"description": "Database id", "type": int},
            "name": {"description": "Table name", "type": str},
        },
        description=f"List of registered tables with pagination. {_DEFAULT_CONTENT_PER_PAGE} tables per page.",
        security="apikey",
    )
    @api.marshal_with(_table_list, code=200, description="table_list")
    @jwt_required()
    def get(self, current_user):
        """List all tables"""
        params = request.args
        return get_tables(current_user=current_user, params=params)


@api.route("/<int:table_id>")
class TableById(Resource):
    @api.doc("Update a table", security="apikey")
    @api.expect(_table_update, validate=True)
    @api.response(200, "table_updated", _default_message_response)
    @api.response(400, "Input payload validation failed", _validation_error_response)
    @api.response(401, "user_unauthorized", _default_message_response)
    @api.response(404, "table_not_found", _default_message_response)
    @api.response(409, "table_already_exist", _default_message_response)
    @jwt_required()
    def put(self, current_user, table_id: int):
        """Update a table"""
        data = request.json
        update_table(current_user=current_user, table_id=table_id, data=data)
        return {"message": "table_updated"}, 200

    @api.doc("Delete a table", security="apikey")
    @api.response(200, "table_deleted", _default_message_response)
    @api.response(401, "user_unauthorized", _default_message_response)
    @api.response(404, "table_not_found", _default_message_response)
    @jwt_required()
    def delete(self, current_user, table_id: int):
        """Delete a table"""
        delete_table(current_user=current_user, table_id=table_id)
        return {"message": "table_deleted"}, 200

    @api.doc("Get table by id", security="apikey")
    @api.marshal_with(_table_response, code=200, description="Table info")
    @api.response(401, "user_unauthorized", _default_message_response)
    @api.response(404, "table_not_found", _default_message_response)
    @jwt_required()
    def get(self, current_user, table_id: int):
        """Get table by id"""
        return get_table_by_id(current_user=current_user, table_id=table_id)


@api.route("/<int:database_id>")
class TableByDatabaseId(Resource):
    @api.doc("Creates a new table", security="apikey")
    @api.expect(_table_post, validate=True)
    @api.response(201, "table_created", _default_message_response)
    @api.response(400, "Input payload validation failed", _validation_error_response)
    @api.response(401, "user_unauthorized", _default_message_response)
    @api.response(404, "database_not_found", _default_message_response)
    @api.response(409, "table_already_exist", _default_message_response)
    @jwt_required()
    def post(self, current_user, database_id):
        """Creates a new table"""
        data = request.json
        save_new_table(current_user=current_user, database_id=database_id, data=data)
        return {"message": "table_created"}, 201
