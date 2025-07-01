from flask import render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
from app.models import User, Prediction, Feedback
from app.main import bp
from app.main.forms import EditProfileForm, FeedbackForm  # Добави този импорт
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
    user = User.query.filter_by(username=username).first_or_404()

    # --- НАЧАЛО НА ПРОМЯНАТА ---
    # Правим изрична, директна заявка към таблицата Prediction,
    # вместо да използваме user.predictions
    predictions = Prediction.query.filter_by(user_id=user.id).order_by(Prediction.timestamp.desc()).all()
    # ---------------------------

    # Дебъг принт, за да сме сигурни
    print(f"DEBUG (директна заявка): Намерени предсказания: {predictions}")

    return render_template('main/user_profile.html',
                           user=user,
                           predictions=predictions,
                           title=f"Профил на {user.username}")

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

@bp.route('/feedback', methods=['GET', 'POST'])
@login_required
def feedback():
    form = FeedbackForm()
    if form.validate_on_submit():
        new_feedback = Feedback(
            rating=int(form.rating.data),
            comment=form.comment.data,
            author=current_user
        )
        db.session.add(new_feedback)
        db.session.commit()
        flash('Благодарим за вашия отзив!', 'success')
        return redirect(url_for('main.index'))
    return render_template('main/feedback.html', title='Оставете отзив', form=form)


@bp.route('/reviews')
def reviews():
    # Извличаме всички отзиви, сортирани по дата (най-новите първи)
    # .join(User) прави оптимизация, за да зареди и данните за автора с една заявка
    all_feedback = Feedback.query.join(User).order_by(Feedback.timestamp.desc()).all()

    return render_template('main/reviews.html',
                           title='Отзиви от нашите потребители',
                           feedbacks=all_feedback)