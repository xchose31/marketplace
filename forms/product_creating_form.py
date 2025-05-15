from flask_wtf import FlaskForm
from wtforms.fields import EmailField, PasswordField, SubmitField, BooleanField, StringField, FileField, IntegerField
from wtforms.validators import DataRequired

class ProductForm(FlaskForm):
    name = StringField('Название товара', validators=[DataRequired()])
    description = StringField('Описание товара', validators=[DataRequired()])
    category = StringField("Категория товара", validators=[DataRequired()])
    logo = FileField('Картинка товара', validators=[DataRequired()])
    stock_quantity = IntegerField('Количество товара', validators=[DataRequired()])
    price = IntegerField("Цена товара за штуку", validators=[DataRequired()])
    submit = SubmitField('Создать товар')