from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, EmailField, DecimalField, SubmitField
from wtforms.validators import DataRequired


class RegisterForm(FlaskForm):
    name = StringField('Имя', [DataRequired()])
    surname = StringField('Фамилия', [DataRequired()])
    address = StringField('Домашний адрес', [DataRequired()])
    phone_number = StringField('Номер телефона', validators=[DataRequired()])
    email = EmailField('Почта', [DataRequired()])
    password = PasswordField('Пароль', [DataRequired()])
    password_again = PasswordField('Повтори пароль', [DataRequired()])
    submit = SubmitField('Зарегистрироваться')