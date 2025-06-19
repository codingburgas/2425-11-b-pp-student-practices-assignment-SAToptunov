from flask import render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
from app.models import User
from app.main import bp
from app.main.forms import EditProfileForm # Добави този импорт
from flask_login import current_user
from app import db

@bp.route('/')
@bp.route('/index')
def index():
    # x = 1 / 0  # Това ще предизвика ZeroDivisionError

    return render_template('index.html', title='Начало')


@bp.route('/user/<username>')
@login_required
def user_profile(username):
    # Намираме потребителя в базата данни по потребителско име.
    # first_or_404() автоматично ще върне 404 грешка, ако потребителят не е намерен.
    user = User.query.filter_by(username=username).first_or_404()

    # Можем да подадем и някакви данни, например списък с неговите "анкети"
    # posts = user.posts.order_by(Post.timestamp.desc()).all() # (Пример)

    return render_template('main/user_profile.html', user=user, title=f"Профил на {user.username}")

@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()

    # Ако формата е изпратена (POST заявка)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Промените са запазени успешно!', 'success')
        return redirect(url_for('main.user_profile', username=current_user.username))

    # Ако страницата се зарежда за първи път (GET заявка)
    # Попълваме формата с текущите данни на потребителя
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email

    return render_template('main/edit_profile.html', title='Редакция на профил', form=form)