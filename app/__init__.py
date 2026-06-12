from datetime import timedelta

from flask import Flask
from flask_migrate import Migrate

from .extensions import db, migrate

def create_app():
    app = Flask(__name__)

    app.config.from_pyfile('config.py')

    db.init_app(app)
    migrate.init_app(app, db)

    from app.routes.auth import init_login_manager
    init_login_manager(app)

    from app.routes.auth import bp as auth_bp
    from app.routes.index import bp as index_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(index_bp)

    return app