# -*- coding: utf-8 -*-

# инициализация приложения:
# - создант и настраивает Flask
# - инициализирует расширения
# - импорт моделей и маршрутов в приложение

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = "main.login_page"


def create_app(config_class=Config):

    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)

    from app.routes import main_bp

    app.register_blueprint(main_bp)

    from app import models

    @login.user_loader
    def load_user(user_id):
        return db.session.get(models.User, int(user_id))

    return app
