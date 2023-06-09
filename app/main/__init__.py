from faker import Faker
from flask import Flask
from flask.app import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

from app.main.config import config_by_name

db = SQLAlchemy()
app = Flask(__name__)
faker = Faker(locale=["pt_BR"])
CORS(app)


def create_app(config_name: str) -> Flask:
    app.config.from_object(config_by_name[config_name])
    db.init_app(app)

    return app
