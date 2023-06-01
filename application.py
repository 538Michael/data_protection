import logging
import os
import sys

sys.stdout.flush()
from logging.handlers import RotatingFileHandler

from werkzeug.exceptions import HTTPException

import app.main.model
from app import blueprint
from app.main import create_app, db
from seeder import create_seed

env_name = os.environ.get("ENV_NAME", "dev")

app = create_app(env_name)
app.register_blueprint(blueprint)


# Global Exception Error
@app.errorhandler(Exception)
def handle_exception(error):
    print(error)
    if isinstance(error, HTTPException):
        return {
            "error": {"message": str(error)},
        }, error.code
    return {
        "error": {
            "message": str(error),
        }
    }, 200


app.app_context().push()

formatter = logging.Formatter(
    "[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s"
)
handler = RotatingFileHandler("data_protection.log", maxBytes=10000000, backupCount=5)
handler.setLevel(logging.DEBUG)
handler.setFormatter(formatter)
app.logger.addHandler(handler)


@app.cli.command("create_db")
def create_db():
    db.drop_all()
    db.create_all()
    db.session.commit()

    if env_name in ["dev", "staging"]:
        create_seed()


if __name__ == "__main__":
    app.run(host=app.config["HOST"])
