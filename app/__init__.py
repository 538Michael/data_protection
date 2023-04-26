from flask import Blueprint
from flask_restx import Api

from app.main.controller import user_ns
from app.main.exceptions import DefaultException, ValidationException
from app.main.util import DefaultResponsesDTO

blueprint = Blueprint("api", __name__)

authorizations = {
    "api_key": {"type": "apiKey", "in": "header", "name": "x-access-token"}
}


api = Api(
    blueprint,
    authorizations=authorizations,
    title="Data Protection based on Anonymization Techniques",
    version="1.0",
    description="Back-end",
    security="apikey",
)

api.add_namespace(user_ns, path="/user")

api.add_namespace(DefaultResponsesDTO.api)

# Exception Handler
api.errorhandler(DefaultException)


@api.errorhandler(ValidationException)
def handle_validation_exception(error):
    """Return a list of errors and a message"""
    return {"errors": error.errors, "message": error.message}, error.code
