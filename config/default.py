import os


# ==========================================
# BASE DIRECTORY
# ==========================================

BASE_DIR = os.path.abspath(
    os.path.dirname(
        os.path.dirname(__file__)
    )
)


# ==========================================
# DATABASE DIRECTORY
# ==========================================

DATA_DIR = os.path.join(BASE_DIR, "data")

# Create data directory automatically
os.makedirs(DATA_DIR, exist_ok=True)


# ==========================================
# DATABASE PATH
# ==========================================

DATABASE_PATH = os.path.join(
    DATA_DIR,
    "yatrik.db"
)


# ==========================================
# BASE CONFIG
# ==========================================

class Config:

    # --------------------------------------
    # Secret Key
    # --------------------------------------

    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "yatrik-dev-secret-key"
    )


    # --------------------------------------
    # Database
    # --------------------------------------

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL"
    ) or f"sqlite:///{DATABASE_PATH}"


    SQLALCHEMY_TRACK_MODIFICATIONS = False


    # --------------------------------------
    # Flask
    # --------------------------------------

    DEBUG = False
    TESTING = False


# ==========================================
# DEVELOPMENT CONFIG
# ==========================================

class DevelopmentConfig(Config):

    DEBUG = True


# ==========================================
# PRODUCTION CONFIG
# ==========================================

class ProductionConfig(Config):

    DEBUG = False


# ==========================================
# CONFIG MAP
# ==========================================

config_map = {

    "development": DevelopmentConfig,

    "production": ProductionConfig,

    "default": DevelopmentConfig

}