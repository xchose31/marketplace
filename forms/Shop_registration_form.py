from flask_wtf import FlaskForm
from wtforms.fields import EmailField, PasswordField, SubmitField, BooleanField, StringField, FileField
from wtforms.validators import DataRequired


class Shop_registration(FlaskForm):
    name = StringField('Название магазина', validators=[DataRequired()])
    description = StringField('Описание магазина', validators=[DataRequired()])
    logo = FileField('Логотип', validators=[DataRequired()])
    submit = SubmitField('Зарегистрировать', validators=[DataRequired()])