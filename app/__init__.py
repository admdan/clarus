from flask import Flask
from .db import get_db_connection

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    with app.app_context():
        from . import routes, management
        app.register_blueprint(routes.bp)
        app.register_blueprint(management.troubleshooting_bp)

    return app
