# app/email.py
from flask import render_template, url_for, current_app
from flask_mail import Message
from app import mail
from itsdangerous import URLSafeTimedSerializer


def send_confirmation_email(user_email):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    token = serializer.dumps(user_email, salt='email-confirmation-salt')

    confirm_url = url_for('auth.confirm_email', token=token, _external=True)

    msg = Message(
        'Потвърждение на имейл - Spam Classifier',
        # Използвай ADMINS, защото MAIL_USERNAME може да е празен
        sender=current_app.config['ADMINS'][0],
        recipients=[user_email]
    )
    msg.html = render_template(
        'email/confirm_email.html',
        confirm_url=confirm_url
    )
    mail.send(msg)