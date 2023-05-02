from flask import request
from flask_restx import Resource

from app.main.service import change_password, jwt_required
from app.main.util import DefaultResponsesDTO, PasswordDTO

password_ns = PasswordDTO.api
api = password_ns
password_change = PasswordDTO.password_change

_default_message_response = DefaultResponsesDTO.message_response


@api.route("/change/<int:user_id>")
class ChangePassword(Resource):
    @api.doc("Change password", security="apikey")
    @api.expect(password_change, validate=True)
    @api.response(200, "password_updated", _default_message_response)
    @api.response(400, "Input payload validation failed", _default_message_response)
    @api.response(404, "user_not_found", _default_message_response)
    @api.response(
        409,
        "password_not_match\npassword_incorrect_information",
        _default_message_response,
    )
    @jwt_required()
    def patch(self, user_id: int) -> tuple[dict[str, str], int]:
        """Change password when logged in"""
        data = request.json
        change_password(data=data, user_id=user_id)
        return {"message": "password_updated"}, 200
