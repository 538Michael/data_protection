from flask import request
from flask_restx import Resource

from app.main.config import Config
from app.main.model import User
from app.main.service import get_user_by_id, get_users, jwt_required, save_new_user
from app.main.util import DefaultResponsesDTO, UserDTO

user_ns = UserDTO.api
api = user_ns
_user_post = UserDTO.user_post
_user_list = UserDTO.user_list
_user_response = UserDTO.user_response


_default_message_response = DefaultResponsesDTO.message_response

_CONTENT_PER_PAGE = Config.CONTENT_PER_PAGE
_DEFAULT_CONTENT_PER_PAGE = Config.DEFAULT_CONTENT_PER_PAGE


@api.route("")
class User(Resource):
    @api.doc(
        "List users with pagination",
        params={
            "page": {"description": "Page number", "default": 1, "type": int},
            "per_page": {
                "description": "Items per page",
                "default": _DEFAULT_CONTENT_PER_PAGE,
                "enum": _CONTENT_PER_PAGE,
                "type": int,
            },
            "name": {"description": "User name", "type": str},
        },
        description=f"List of users with pagination. {_DEFAULT_CONTENT_PER_PAGE} users per page.",
        security="apikey",
    )
    @api.marshal_with(_user_list, code=200, description="users_list ")
    @jwt_required(admin_check=True)
    def get(self, current_user):
        """List all registered users"""
        params = request.args
        return get_users(params=params)

    @api.doc("Create new user")
    @api.expect(_user_post, validate=True)
    @api.response(201, "user_created", _default_message_response)
    @api.response(409, "name_in_use", _default_message_response)
    def post(self) -> tuple[dict[str, str], int]:
        """Creates a new user"""
        data = request.json
        save_new_user(data=data)
        return {"message": "user_created"}, 201


@api.route("/<int:user_id>")
class UserWithId(Resource):
    """User routes with id"""

    @api.doc("Get user by id", security="apikey")
    @api.response(200, "user_updated", _default_message_response)
    @api.response(404, "user_not_found", _default_message_response)
    @api.marshal_with(_user_response, code=200, description="User Info")
    @jwt_required()
    def get(self, current_user, user_id: int):
        """Get user by id"""
        return get_user_by_id(user_id)
