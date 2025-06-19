# app/classifier/forms.py

from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.validators import DataRequired

class ClassifierForm(FlaskForm):
    message_text = TextAreaField(
        'Текст на съобщението',
        validators=[DataRequired(message="Полето не може да бъде празно.")]
    )

    submit = SubmitField('Класифицирай')