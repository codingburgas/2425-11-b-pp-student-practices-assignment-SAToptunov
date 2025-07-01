# app/classifier/routes.py
from flask import render_template, flash, session, redirect, url_for
from app.classifier import bp
from app.classifier.forms import ClassifierForm
from app.classifier.utils import classify_message, get_model_stats
from flask_login import login_required, current_user
from app.models import Prediction # Добави този импорт
from app import db # Добави и този


@bp.route('/classify', methods=['GET', 'POST'])
@login_required
def classify():
    form = ClassifierForm()
    prediction_result = None
    probability_result = None

    # --- НАЧАЛО НА КОРЕКЦИЯТА ---
    # Взимаме статистиките ВИНАГИ, в началото на функцията.
    stats = get_model_stats()
    # ---------------------------

    if form.validate_on_submit():
        message = form.message_text.data
        prediction_result, probability_result = classify_message(message)

        if "Грешка" not in prediction_result:
            flash('Съобщението е класифицирано успешно!', 'success')
            # Тук вече имаме резултат, можем да го покажем
        else:
            flash(prediction_result, 'danger')
            prediction_result = None
            probability_result = None

    # Подаваме всичко към шаблона.
    # `stats` ще бъде подаден и при GET, и при POST заявка.
    return render_template('classifier/classify.html',
                           title='Класификатор',
                           form=form,
                           prediction=prediction_result,
                           probability=probability_result,
                           stats=stats)