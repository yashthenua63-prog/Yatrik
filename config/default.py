import os


BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


class Config:
    # Secret key
    SECRET_KEY = os.environ.get(
        "SECRET_KEY"
    ) or "yatrik-dev-secret-key"


    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL"
    ) or "sqlite:///" + os.path.join(
        BASE_DIR,
        "data",
        "yatrik.db"
    )


    SQLALCHEMY_TRACK_MODIFICATIONS = False


    # Flask
    DEBUG = False
    TESTING = False



class DevelopmentConfig(Config):
    DEBUG = True



class ProductionConfig(Config):
    DEBUG = False



config_map = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig
}