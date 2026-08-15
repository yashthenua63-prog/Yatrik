from flask import Flask, render_template
from config.default import config_map
from app.database import db, migrate

def create_app(config_name="default"):
    """
    Application Factory
    """

    app = Flask(__name__)

    # Load configuration
    app.config.from_object(config_map[config_name])

    # Initialize plugins
    db.init_app(app)
    migrate.init_app(app, db, render_as_batch=True)
    
    from app.auth_manager import login_manager
    login_manager.init_app(app)
    from app.models import Temple

    # Register blueprints
    from app.routes.main import main_bp
    from app.routes.user import user_bp
    from app.routes.planner import planner_bp
    from app.routes.hotels import hotels_bp
    from app.routes.restaurants import restaurants_bp
    from app.routes.ride import ride_bp
    from app.routes.auth import auth_bp
    from app.routes.partner import partner_bp
    from app.routes.static_pages import static_pages_bp
    from app.routes.news import news_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(planner_bp)
    app.register_blueprint(hotels_bp)
    app.register_blueprint(restaurants_bp)
    app.register_blueprint(ride_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(partner_bp)
    app.register_blueprint(static_pages_bp)
    app.register_blueprint(news_bp)
    
    from app.routes.events import events_bp
    from app.routes.food_trails import food_trails_bp
    from app.routes.darshan_planner import darshan_planner_bp
    from app.routes.braj_trip_os import braj_trip_os_bp
    from app.routes.support import support_bp
    from app.routes.destinations import destinations_bp
    
    app.register_blueprint(events_bp)
    app.register_blueprint(food_trails_bp)
    app.register_blueprint(darshan_planner_bp)
    app.register_blueprint(braj_trip_os_bp)
    app.register_blueprint(support_bp)
    app.register_blueprint(destinations_bp)
    
    # Initialize Admin
    from app.routes.admin import setup_admin
    setup_admin(app)
    
    # Register CLI Commands
    from app.cli import register_cli_commands
    register_cli_commands(app)

    @app.route("/health")
    def health():
        return {
            "status": "healthy",
            "project": "Yatrik"
        }

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html'), 403

    @app.errorhandler(500)
    def server_error(e):
        return render_template('errors/500.html'), 500

    return app