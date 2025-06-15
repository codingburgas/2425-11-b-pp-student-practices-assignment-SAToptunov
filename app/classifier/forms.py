# app/classifier/forms.py
from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.validators import DataRequired

class ClassifierForm(FlaskForm):
    message = TextAreaField('Въведете текст на имейл или съобщение',
                            validators=[DataRequired()],
                            render_kw={"rows": 10, "cols": 70})
    submit = SubmitField('Класифицирай')