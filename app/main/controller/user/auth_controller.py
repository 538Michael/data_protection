from flask import request
from flask_restx import Resource

from app.main.service import login
from app.main.util import AuthDTO, DefaultResponsesDTO

auth_ns = AuthDTO.api
api = auth_ns
_auth_login = AuthDTO.auth_login
_auth_response = AuthDTO.auth_response

_default_message_response = DefaultResponsesDTO.message_response
_validation_error_response = DefaultResponsesDTO.validation_error


@api.route("")
class Login(Resource):
    @api.doc("User login")
    @api.expect(_auth_login, validate=True)
    @api.response(401, "password_incorrect_information", _default_message_response)
    @api.response(400, "Input payload validation failed", _validation_error_response)
    @api.marshal_with(_auth_response, code=200, description="user_logged_in")
    def post(self):
        """User login"""
        data = request.json
        return login(data=data)
