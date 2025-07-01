# app/auth/routes.py
from flask import render_template, flash, redirect, url_for, request, current_app
from app import db
from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm
from flask_login import login_user, logout_user, current_user, login_required
from app.models import User, Role
from urllib.parse import urlsplit
from app.email import send_confirmation_email
from itsdangerous import URLSafeTimedSerializer
from sqlalchemy import or_


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        # --- НАЧАЛО НА ПРОМЕНИТЕ В ЛОГИКАТА ---

        # 1. Взимаме въведената стойност
        login_identifier = form.username.data

        # 2. Правим заявка, която търси или по username, или по email
        # .ilike() прави търсенето нечувствително към малки/големи букви
        user = User.query.filter(
            or_(
                User.username.ilike(login_identifier),
                User.email.ilike(login_identifier)
            )
        ).first()

        # 3. Проверяваме дали е намерен потребител и дали паролата е вярна
        if user is None or not user.check_password(form.password.data):
            flash('Невалидно потребителско име, имейл или парола.', 'danger')
            return redirect(url_for('auth.login'))

        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('main.index')
        flash(f'Добре дошли отново, {user.username}!', 'success')
        return redirect(next_page)
    return render_template('auth/login.html', title='Вход', form=form)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        # Изпращаме имейла за потвърждение
        send_confirmation_email(user.email)

        flash('Регистрацията е успешна! Моля, проверете имейла си, за да потвърдите акаунта си.')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', title='Регистрация', form=form)


@bp.route('/confirm/<token>')
@login_required
def confirm_email(token):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = serializer.loads(token, salt='email-confirmation-salt', max_age=3600)
    except:
        flash('Линкът за потвърждение е невалиден или е изтекъл.', 'danger')
        return redirect(url_for('main.index'))

    if email != current_user.email:
        flash('Не можете да потвърдите този имейл адрес.', 'danger')
        return redirect(url_for('main.index'))

    if current_user.email_confirmed:
        flash('Акаунтът вече е потвърден.', 'info')
    else:
        current_user.email_confirmed = True
        db.session.add(current_user)
        db.session.commit()
        flash('Успешно потвърдихте своя имейл адрес!', 'success')

    return redirect(url_for('main.index'))


@bp.route('/resend_confirmation')
@login_required
def resend_confirmation_email():
    if current_user.email_confirmed:
        flash('Твоят имейл вече е потвърден.', 'info')
        return redirect(url_for('main.index'))

    # Извикваме същата функция, която използваме и при регистрация
    send_confirmation_email(current_user.email)
    flash('Изпратен е нов линк за потвърждение на твоя имейл адрес.', 'success')
    return redirect(url_for('main.user_profile', username=current_user.username))