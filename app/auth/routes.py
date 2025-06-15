# app/auth/routes.py
from flask import render_template, flash, redirect, url_for, request
from app import db
from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm
from flask_login import current_user, login_user, logout_user
from app.models import User, Role
from urllib.parse import urlsplit


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Невалидно потребителско име или парола', 'danger')
            return redirect(url_for('auth.login'))

        # Тук можем да добавим проверка дали имейлът е потвърден
        # if not user.confirmed:
        #     flash('Моля, потвърдете имейл адреса си.', 'warning')
        #     return redirect(url_for('auth.login'))

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

        # Присвояване на роля 'User' по подразбиране
        user_role = Role.query.filter_by(name='User').first()
        user.role = user_role

        db.session.add(user)
        db.session.commit()
        flash('Поздравления, вие се регистрирахте успешно!', 'success')
        # TODO: Добави логика за изпращане на имейл за потвърждение
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', title='Регистрация', form=form)