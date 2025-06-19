# app/models.py
import hashlib
from datetime import datetime
from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from itsdangerous import URLSafeTimedSerializer as Serializer
from flask import current_app


# Таблица за връзка "много-към-много" между потребители и роли (макар че ние ще ползваме "един-към-много")
# Тук е дефинирана за бъдещи разширения. Засега ще сложим role_id директно в User.

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = ['User', 'Admin']
        for r_name in roles:
            role = Role.query.filter_by(name=r_name).first()
            if role is None:
                role = Role(name=r_name)
                db.session.add(role)
        db.session.commit()


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    email_confirmed = db.Column(db.Boolean, nullable=False, default=False)

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config.get('ADMINS', [''])[0]:
                self.role = Role.query.filter_by(name='Admin').first()
            if self.role is None:
                self.role = Role.query.filter_by(name='User').first()

    def is_admin(self):
        return self.role is not None and self.role.name == 'Admin'

    # Поле за потвърждение на имейла
    confirmed = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_gravatar_hash(self, email_text):
        return hashlib.md5(email_text.lower().encode('utf-8')).hexdigest()

    # Методи за генериране и проверка на токен за потвърждение на имейл
    def generate_confirmation_token(self):
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'confirm': self.id})

    def confirm(self, token, max_age=3600):  # Токенът е валиден 1 час
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token, max_age=max_age)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def __repr__(self):
        return f'<User {self.username}>'


# Тази функция се изисква от Flask-Login, за да зарежда потребител от сесията
@login.user_loader
def load_user(id):
    return User.query.get(int(id))