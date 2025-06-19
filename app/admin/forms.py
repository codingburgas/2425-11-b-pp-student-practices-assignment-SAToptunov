from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email

class EditUserProfileAdminForm(FlaskForm):
    username = StringField('Потребителско име', validators=[DataRequired()])
    email = StringField('Имейл', validators=[DataRequired(), Email()])
    role = SelectField('Роля', coerce=int)
    submit = SubmitField('Запази')

    def __init__(self, user, *args, **kwargs):
        super(EditUserProfileAdminForm, self).__init__(*args, **kwargs)
        # Попълваме списъка с роли от базата данни
        from app.models import Role
        self.role.choices = [(role.id, role.name) for role in Role.query.order_by(Role.name).all()]
        self.user = user