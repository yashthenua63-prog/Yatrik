import os
from app import create_app

# Development environment by default
config_env = os.getenv("FLASK_ENV") or "default"

# Create Flask application
app = create_app(config_env)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)