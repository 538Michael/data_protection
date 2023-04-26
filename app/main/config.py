import os

# uncomment the line below for postgres database url from environment variable
# postgres_local_base = os.environ['DATABASE_URL']

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "my_precious_secret_key")
    DEBUG = False
    JWT_EXP = 8
    ACTIVATION_EXP_SECONDS = 86400

    # Remove additional message on 404 responses
    RESTX_ERROR_404_HELP = False

    # Swagger
    RESTX_MASK_SWAGGER = False

    # Pagination
    CONTENT_PER_PAGE = [5, 10, 20, 30, 50, 100]
    DEFAULT_CONTENT_PER_PAGE = CONTENT_PER_PAGE[1]

    # The maximum file size for upload
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 megas


class DevelopmentConfig(Config):
    # uncomment the line below to use postgres
    # SQLALCHEMY_DATABASE_URI = postgres_local_base
    postgres_local_base = (
        "postgresql+psycopg2://postgres:postgres@localhost/data_protection"
    )
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = postgres_local_base
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ENV = "development"
    HOST = "localhost"

    # uncomment the line below to see SQLALCHEMY queries
    # SQLALCHEMY_ECHO = True


class StagingConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = (
        "postgresql+psycopg2://postgres:postgres@data_protection_db/data_protection"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ENV = "staging"
    HOST = "0.0.0.0"


class TestingConfig(Config):
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(
        basedir, "flask_boilerplate_test.db"
    )
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ENV = "testing"


class ProductionConfig(Config):
    DEBUG = False
    # uncomment the line below to use postgres
    # SQLALCHEMY_DATABASE_URI = postgres_local_base
    ENV = "production"


config_by_name = dict(
    dev=DevelopmentConfig,
    test=TestingConfig,
    prod=ProductionConfig,
    staging=StagingConfig,
)

_env_name = os.environ.get("ENV_NAME")
_env_name = _env_name if _env_name is not None else "dev"
app_config = config_by_name[_env_name]
