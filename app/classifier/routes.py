# app/classifier/routes.py
from flask import render_template, flash, session
from app.classifier import bp
from app.classifier.forms import ClassifierForm
from app.classifier.utils import classify_message
from flask_login import login_required


@bp.route('/classify', methods=['GET', 'POST'])
@login_required  # Само логнати потребители могат да класифицират
def classify():
    form = ClassifierForm()
    prediction = None
    probability = None

    if form.validate_on_submit():
        message = form.message.data
        prediction, probability = classify_message(message)
        flash(f'Съобщението е класифицирано!', 'success')

        # Съхраняваме резултата в сесията, за да го покажем на същата страница
        session['prediction_result'] = {
            'message': message,
            'prediction': prediction,
            'probability': f"{probability * 100:.2f}%"
        }

    # Взимаме резултата от сесията, ако има такъв
    result = session.pop('prediction_result', None)

    return render_template('classifier/classify.html',
                           title='Spam Класификатор',
                           form=form,
                           result=result)