# app/classifier/routes.py
from flask import render_template, flash, session, redirect, url_for
from app.classifier import bp
from app.classifier.forms import ClassifierForm
from app.classifier.utils import classify_message
from flask_login import login_required, current_user


@bp.route('/classify', methods=['GET', 'POST'])
@login_required
def classify():
    if not current_user.email_confirmed:
        flash('Моля, първо потвърдете своя имейл адрес, за да използвате тази функционалност.', 'warning')
        return redirect(url_for('main.index'))

    form = ClassifierForm()
    prediction = None
    probability = None

    if form.validate_on_submit():
        message = form.message_text.data
        prediction, probability = classify_message(message)

        # --- КОРЕКЦИЯ НА ЛОГИКАТА ---
        # Проверяваме дали предсказанието НЕ е съобщение за грешка
        if "Грешка" not in prediction:
            flash('Съобщението е класифицирано успешно!', 'success')  # Променяме на 'success' за зелен цвят
        else:
            # Ако има грешка, показваме нея като flash съобщение
            flash(prediction, 'danger')
            # Нулираме променливите, за да не се показва блокът с резултат
            prediction = None
            probability = None
        # ---------------------------------

    return render_template('classifier/classify.html',
                           title='Класификатор',
                           form=form,
                           prediction=prediction,
                           probability=probability)