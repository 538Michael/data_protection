from flask_restx import Resource

from app.main.service import delete_anonymization, save_new_anonymization
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
    @api.response(404, "table_not_found", _default_message_response)
    @api.response(
        409,
        "database_not_exists\ntable_not_exists\ntable_already_anonymized",
        _default_message_response,
    )
    def post(self, table_id):
        """Creates a new anonymization"""
        save_new_anonymization(table_id=table_id)
        return {"message": "anonymization_created"}, 201

    @api.doc("Delete a anonymization")
    @api.response(200, "anonymization_deleted", _default_message_response)
    @api.response(404, "table_not_found", _default_message_response)
    @api.response(
        409,
        "database_not_exists\ncloud_database_not_exists\ntable_not_anonymized\ntable_not_exists",
        _default_message_response,
    )
    def delete(self, table_id):
        """Delete a anonymization"""
        delete_anonymization(table_id=table_id)
        return {"message": "anonymization_deleted"}, 200
