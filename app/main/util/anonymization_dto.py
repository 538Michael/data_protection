from flask_restx import Namespace


class AnonymizationDTO:
    api = Namespace("anonymization", description="anonymization related operations")
