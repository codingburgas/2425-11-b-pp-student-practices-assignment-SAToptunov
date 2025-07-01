# app/auth/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from app.models import User

class LoginForm(FlaskForm):
    # --- ПРОМЯНА НА ЕТИКЕТА ---
    username = StringField('Потребителско име или Имейл', validators=[DataRequired()])
    # ---------------------------
    password = PasswordField('Парола', validators=[DataRequired()])
    remember_me = BooleanField('Запомни ме')
    submit = SubmitField('Вход')

class RegistrationForm(FlaskForm):
    username = StringField('Потребителско име', validators=[DataRequired()])
    email = StringField('Имейл', validators=[DataRequired(), Email()])
    password = PasswordField('Парола', validators=[DataRequired()])
    password2 = PasswordField(
        'Повтори паролата', validators=[DataRequired(), EqualTo('password', message='Паролите трябва да съвпадат.')])
    submit = SubmitField('Регистрация')

    # Персонализирани валидатори, които проверяват дали потребителското име или имейлът вече са заети
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Това потребителско име вече е заето. Моля, изберете друго.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Този имейл адрес вече се използва. Моля, използвайте друг.')