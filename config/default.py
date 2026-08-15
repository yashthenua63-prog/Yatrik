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
os.makedirs(DATA_DIR, exist_ok=True)

DATABASE_PATH = os.path.join(DATA_DIR, "yatrik.db")


# ==========================================
# PRIVATE UPLOADS
# ==========================================

PRIVATE_UPLOADS_PATH = os.path.join(BASE_DIR, "private_uploads")
os.makedirs(PRIVATE_UPLOADS_PATH, exist_ok=True)


# ==========================================
# BASE CONFIG
# ==========================================

class Config:

    # Secret Key — MUST be set in production via env variable
    SECRET_KEY = os.environ.get("SECRET_KEY", "yatrik-dev-secret-key-change-in-prod")

    # Database
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("DATABASE_URL") or f"sqlite:///{DATABASE_PATH}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Private uploads
    PRIVATE_UPLOADS_PATH = os.environ.get("PRIVATE_UPLOADS_PATH", PRIVATE_UPLOADS_PATH)

    # Session Security
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_DURATION = 86400 * 30  # 30 days

    # File upload limits
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10 MB max upload

    # Flask defaults
    DEBUG = False
    TESTING = False

    # Base URL for SEO and Sitemap
    BASE_URL = os.environ.get("BASE_URL", "https://yatrik-rw1u.onrender.com")


# ==========================================
# DEVELOPMENT CONFIG
# ==========================================

class DevelopmentConfig(Config):
    DEBUG = True
    SESSION_COOKIE_SECURE = False   # HTTP is fine in dev


# ==========================================
# PRODUCTION CONFIG
# ==========================================

class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True    # HTTPS required
    SESSION_COOKIE_HTTPONLY = True
    PREFERRED_URL_SCHEME = "https"


# ==========================================
# TESTING CONFIG
# ==========================================

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False
    SECRET_KEY = "test-secret-key"
    LOGIN_DISABLED = False


# ==========================================
# CONFIG MAP
# ==========================================

config_map = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}