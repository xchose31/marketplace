from flask_wtf import FlaskForm
from wtforms.fields import EmailField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired


class Login_user_form(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня', validators=[DataRequired()])
    submit = SubmitField('Войти')