from flask import Flask
from .db import get_db_connection
from flask_login import LoginManager
from .models import get_user
from .asset import asset_bp
from .profile import profile_bp
from .role import role
from .eip import eip_bp
from .routes import bp
from .troubleshooting import troubleshooting_bp

login_manager=LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    app.secret_key = app.config['SECRET_KEY']

    app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5 MB for file upload

    login_manager.init_app(app)
    login_manager.login_view = 'routes.login_register'

    @login_manager.user_loader
    def load_user(user_id):
        return get_user(user_id)

    with app.app_context():
        app.register_blueprint(bp)
        app.register_blueprint(troubleshooting_bp)
        app.register_blueprint(asset_bp)
        app.register_blueprint(profile_bp)
        app.register_blueprint(role)
        app.register_blueprint(eip_bp)

    @app.after_request
    def add_cache_control_headers(response):
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    return app
