from flask_restx import Resource

from app.main.service import save_new_anonymization
from app.main.util import AnonymizationDTO, DefaultResponsesDTO

anonymization_ns = AnonymizationDTO.api
api = anonymization_ns

_default_message_response = DefaultResponsesDTO.message_response
_validation_error_response = DefaultResponsesDTO.validation_error


@api.route("/<int:table_id>")
class AnonymizationByTableId(Resource):
    @api.doc("Creates a new anonymization")
    @api.response(201, "anonymization_created", _default_message_response)
    @api.response(400, "Input payload validation failed", _validation_error_response)
    @api.response(404, "user_not_found", _default_message_response)
    @api.response(409, "anonymization_already_exist", _default_message_response)
    def post(self, table_id):
        """Creates a new anonymization"""
        save_new_anonymization(table_id=table_id)
        return {"message": "anonymization_created"}, 201
