from flask import Flask, render_template
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from flask_mail import Mail

# Инстанциите на разширенията се създават "празни"
db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'
login.login_message = 'Моля, влезте в профила си, за да достъпите тази страница.'
bootstrap = Bootstrap()
mail = Mail()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Инициализираме всички разширения, С изключение на Bootstrap
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    mail.init_app(app)

    # --- КЛЮЧОВАТА ПРОМЯНА Е ТУК ---
    # Инициализираме Bootstrap САМО ако НЕ сме в тестов режим.
    # Това заобикаля проблема с 'bootstrap_find_resource' по време на тестове.
    if not app.config.get('TESTING', False):
        bootstrap.init_app(app)
    # --------------------------------

    # Регистрираме Blueprints
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.classifier import bp as classifier_bp
    app.register_blueprint(classifier_bp)

    # Дефинираме глобални Error Handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        db.session.rollback()
        return render_template('500.html'), 500

    return app


# Импортираме моделите най-отдолу, за да са видими за Flask-Migrate
from app import models