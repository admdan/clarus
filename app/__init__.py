from flask import Flask
from .db import get_db_connection
from flask_login import LoginManager
from .models import get_user

login_manager=LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    app.secret_key = app.config['SECRET_KEY']

    login_manager.init_app(app)
    login_manager.login_view = 'routes.login_register'

    @login_manager.user_loader
    def load_user(user_id):
        return get_user(user_id)

    with app.app_context():
        from . import routes, management
        app.register_blueprint(routes.bp)
        app.register_blueprint(management.troubleshooting_bp)

    @app.after_request
    def add_cache_control_headers(response):
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    return app
