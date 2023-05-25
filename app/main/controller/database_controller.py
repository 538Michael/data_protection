from flask import request
from flask_restx import Resource

from app.main.config import Config
from app.main.model import DATABASE_TYPE
from app.main.service import (
    delete_database,
    get_database,
    get_databases,
    save_new_database,
    update_database,
)
from app.main.util import DatabaseDTO, DefaultResponsesDTO

database_ns = DatabaseDTO.api
api = database_ns
_database_post = DatabaseDTO.database_post
_database_update = DatabaseDTO.database_update
_database_response = DatabaseDTO.database_response
_database_list = DatabaseDTO.database_list

_default_message_response = DefaultResponsesDTO.message_response
_validation_error_response = DefaultResponsesDTO.validation_error

_CONTENT_PER_PAGE = Config.CONTENT_PER_PAGE
_DEFAULT_CONTENT_PER_PAGE = Config.DEFAULT_CONTENT_PER_PAGE


@api.route("")
class Database(Resource):
    @api.doc(
        "List databases with pagination",
        params={
            "page": {"description": "Page number", "default": 1, "type": int},
            "per_page": {
                "description": "Items per page",
                "default": _DEFAULT_CONTENT_PER_PAGE,
                "enum": _CONTENT_PER_PAGE,
                "type": int,
            },
            "user_id": {"description": "Database user id", "type": int},
            "type": {
                "description": "Database type",
                "type": str,
                "enum": DATABASE_TYPE,
            },
            "username": {"description": "Database username", "type": str},
            "host": {"description": "Database host", "type": str},
            "port": {"description": "Database port", "type": int},
            "name": {"description": "Database name", "type": str},
        },
        description=f"List of registered databases with pagination. {_DEFAULT_CONTENT_PER_PAGE} databases per page.",
    )
    @api.marshal_with(_database_list, code=200, description="database_list")
    def get(self):
        """List all databases"""
        params = request.args
        return get_databases(params=params)

    @api.doc("Creates a new database")
    @api.expect(_database_post, validate=True)
    @api.response(201, "database_created", _default_message_response)
    @api.response(400, "Input payload validation failed", _validation_error_response)
    @api.response(404, "user_not_found", _default_message_response)
    @api.response(409, "database_already_exist", _default_message_response)
    def post(self):
        """Creates a new database"""
        data = request.json
        save_new_database(data=data)
        return {"message": "database_created"}, 201


@api.route("/<int:database_id>")
class DatabaseById(Resource):
    @api.doc("Update a database")
    @api.expect(_database_update, validate=True)
    @api.response(200, "database_updated", _default_message_response)
    @api.response(400, "Input payload validation failed", _validation_error_response)
    @api.response(404, "database_not_found", _default_message_response)
    @api.response(409, "database_already_exist", _default_message_response)
    def put(self, database_id):
        """Update a database"""
        data = request.json
        update_database(database_id=database_id, data=data)
        return {"message": "database_updated"}, 200

    @api.doc("Delete a database")
    @api.response(200, "database_deleted", _default_message_response)
    @api.response(404, "database_not_found", _default_message_response)
    def delete(self, database_id):
        """Delete a database"""
        delete_database(database_id=database_id)
        return {"message": "database_deleted"}, 200

    @api.doc("Get database by id")
    @api.marshal_with(_database_response, code=200, description="Database info")
    @api.response(404, "database_not_found", _default_message_response)
    def get(self, database_id: int):
        """Get database by id"""
        return get_database(database_id=database_id)
