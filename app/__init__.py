# app/__init__.py
from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from flask_mail import Mail

# Инициализация на разширенията
db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login' # Къде да препрати, ако потребителят не е логнат
login.login_message = 'Моля, влезте в профила си, за да достъпите тази страница.'
bootstrap = Bootstrap()
mail = Mail()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Свързване на разширенията с приложението
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    bootstrap.init_app(app)
    mail.init_app(app)

    # Регистриране на Blueprints
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.classifier import bp as classifier_bp
    app.register_blueprint(classifier_bp)

    return app

# Импортираме моделите тук, за да са видими за Flask-Migrate
from app import models