from flask import Blueprint
from flask_restx import Api

from app.main.controller import auth_ns, database_ns, password_ns, table_ns, user_ns
from app.main.exceptions import DefaultException, ValidationException
from app.main.util import DefaultResponsesDTO

blueprint = Blueprint("api", __name__)

authorizations = {
    "apikey": {
        "type": "apiKey",
        "in": "header",
        "name": "Authorization",
        "description": "Type in the *'Value'* input box below: **'Bearer &lt;JWT&gt;'**, where JWT is the token",
    }
}


api = Api(
    blueprint,
    authorizations=authorizations,
    title="Data Protection based on Anonymization Techniques",
    version="1.0",
    description="Back-end",
)

api.add_namespace(user_ns, path="/user")
api.add_namespace(auth_ns, path="/user/auth")
api.add_namespace(password_ns, path="/user/password")
api.add_namespace(database_ns, path="/database")
api.add_namespace(table_ns, path="/table")

api.add_namespace(DefaultResponsesDTO.api)

# Exception Handler
api.errorhandler(DefaultException)


@api.errorhandler(ValidationException)
def handle_validation_exception(error):
    """Return a list of errors and a message"""
    return {"errors": error.errors, "message": error.message}, error.code
