from flask import Flask
from config.default import config_map
from app.database import db, migrate

def create_app(config_name="default"):
    """
    Application Factory
    """

    app = Flask(__name__)

    # Load configuration
    app.config.from_object(config_map[config_name])

    # Initialize database
    db.init_app(app)
    migrate.init_app(app, db)
    from app.models import Temple

    # Register blueprints
    from app.routes.main import main_bp
    app.register_blueprint(main_bp)

    @app.route("/health")
    def health():
        return {
            "status": "healthy",
            "project": "Yatrik"
        }

    return app