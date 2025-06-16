from flask import render_template
from flask_login import login_required, current_user
from app.models import User
from app.main import bp

@bp.route('/')
@bp.route('/index')
def index():
    # x = 1 / 0  # Това ще предизвика ZeroDivisionError

    return render_template('index.html', title='Начало')

@bp.route('/user/<username>')
@login_required
def user_profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user_profile.html', user=user, title=f"Профил на {user.username}")