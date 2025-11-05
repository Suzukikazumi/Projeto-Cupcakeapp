from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config


db = SQLAlchemy()

def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_object(Config)
    db.init_app(app)

    from . import models


    from .controllers.auth import bp as auth_bp
    from .controllers.shop import bp as shop_bp
    from .controllers.support import bp as support_bp
    from .controllers.notifications import bp as notifications_bp
    from .controllers.admin import bp as admin_bp


    app.register_blueprint(auth_bp)
    app.register_blueprint(shop_bp)
    app.register_blueprint(support_bp)
    app.register_blueprint(notifications_bp)
    app.register_blueprint(admin_bp)

    with app.app_context():
        db.create_all()

    return app
