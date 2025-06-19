import hashlib

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

    @app.context_processor
    def utility_processor():
        def to_gravatar_hash(email_text):
            if not isinstance(email_text, str):
                return ''
            return hashlib.md5(email_text.lower().encode('utf-8')).hexdigest()

        return dict(to_gravatar_hash=to_gravatar_hash)

    # Регистрираме Blueprints
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.classifier import bp as classifier_bp
    app.register_blueprint(classifier_bp)

    from app.admin import bp as admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')

    # Дефинираме глобални Error Handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        db.session.rollback()
        return render_template('500.html'), 500

    @app.context_processor
    def inject_utility_processor():
        def to_gravatar_hash(email_text):
            return hashlib.md5(email_text.lower().encode('utf-8')).hexdigest()

        return dict(to_gravatar_hash=to_gravatar_hash)

    return app


# Импортираме моделите най-отдолу, за да са видими за Flask-Migrate
from app import models