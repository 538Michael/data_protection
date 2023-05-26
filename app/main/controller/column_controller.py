from flask import request
from flask_restx import Resource

from app.main.config import Config
from app.main.service import (
    delete_column,
    get_column_by_id,
    get_columns,
    jwt_required,
    save_new_column,
    update_column,
)
from app.main.util import ColumnDTO, DefaultResponsesDTO

column_ns = ColumnDTO.api
api = column_ns
_column_post = ColumnDTO.column_post
_column_update = ColumnDTO.column_update
_column_response = ColumnDTO.column_response
_column_list = ColumnDTO.column_list

_default_message_response = DefaultResponsesDTO.message_response
_validation_error_response = DefaultResponsesDTO.validation_error

_CONTENT_PER_PAGE = Config.CONTENT_PER_PAGE
_DEFAULT_CONTENT_PER_PAGE = Config.DEFAULT_CONTENT_PER_PAGE


@api.route("")
class Column(Resource):
    @api.doc(
        "List columns with pagination",
        params={
            "page": {"description": "Page number", "default": 1, "type": int},
            "per_page": {
                "description": "Items per page",
                "default": _DEFAULT_CONTENT_PER_PAGE,
                "enum": _CONTENT_PER_PAGE,
                "type": int,
            },
            "table_id": {"description": "Table id", "type": int},
            "name": {"description": "Column name", "type": str},
        },
        description=f"List of registered columns with pagination. {_DEFAULT_CONTENT_PER_PAGE} columns per page.",
        security="apikey",
    )
    @api.marshal_with(_column_list, code=200, description="column_list")
    @jwt_required()
    def get(self, current_user):
        """List all columns"""
        params = request.args
        return get_columns(current_user=current_user, params=params)


@api.route("/<int:column_id>")
class ColumnById(Resource):
    @api.doc("Update a column", security="apikey")
    @api.expect(_column_update, validate=True)
    @api.response(200, "column_updated", _default_message_response)
    @api.response(400, "Input payload validation failed", _validation_error_response)
    @api.response(401, "user_unauthorized", _default_message_response)
    @api.response(404, "column_not_found", _default_message_response)
    @api.response(409, "column_already_exist", _default_message_response)
    @jwt_required()
    def put(self, current_user, column_id):
        """Update a column"""
        data = request.json
        update_column(current_user=current_user, column_id=column_id, data=data)
        return {"message": "column_updated"}, 200

    @api.doc("Delete a column", security="apikey")
    @api.response(200, "column_deleted", _default_message_response)
    @api.response(401, "user_unauthorized", _default_message_response)
    @api.response(404, "column_not_found", _default_message_response)
    @jwt_required()
    def delete(self, current_user, column_id):
        """Delete a column"""
        delete_column(current_user=current_user, column_id=column_id)
        return {"message": "column_deleted"}, 200

    @api.doc("Get column by id", security="apikey")
    @api.marshal_with(_column_response, code=200, description="Column info")
    @api.response(401, "user_unauthorized", _default_message_response)
    @api.response(404, "column_not_found", _default_message_response)
    @jwt_required()
    def get(self, current_user, column_id: int):
        """Get column by id"""
        return get_column_by_id(current_user=current_user, column_id=column_id)


@api.route("/<int:table_id>")
class ColumnByTableId(Resource):
    @api.doc("Creates a new column", security="apikey")
    @api.expect(_column_post, validate=True)
    @api.response(201, "column_created", _default_message_response)
    @api.response(400, "Input payload validation failed", _validation_error_response)
    @api.response(401, "user_unauthorized", _default_message_response)
    @api.response(404, "table_not_found", _default_message_response)
    @api.response(409, "column_already_exist", _default_message_response)
    @jwt_required()
    def post(self, current_user, table_id):
        """Creates a new column"""
        data = request.json
        save_new_column(current_user=current_user, table_id=table_id, data=data)
        return {"message": "column_created"}, 201
