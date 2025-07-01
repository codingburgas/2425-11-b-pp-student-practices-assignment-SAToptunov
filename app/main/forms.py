# app/main/forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, RadioField, TextAreaField
from wtforms.validators import DataRequired, Email

class EditProfileForm(FlaskForm):
    username = StringField('Потребителско име', validators=[DataRequired()])
    email = StringField('Имейл', validators=[DataRequired(), Email()])
    submit = SubmitField('Запази промените')

class FeedbackForm(FlaskForm):
    rating = RadioField(
        'Вашата оценка',
        choices=[('5', '★★★★★'), ('4', '★★★★'), ('3', '★★★'), ('2', '★★'), ('1', '★')],
        validators=[DataRequired(message="Моля, изберете оценка.")]
    )
    comment = TextAreaField('Вашият коментар (по желание)')
    submit = SubmitField('Изпрати отзив')