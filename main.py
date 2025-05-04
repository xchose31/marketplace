import os

from flask import Flask, render_template, redirect, request, abort, jsonify
from flask_restful import Api
from werkzeug.utils import secure_filename

from data import db_session
from flask_login import login_user, logout_user, LoginManager, login_required, current_user
from forms.RegisterForm import RegisterForm
from forms.Login_user_form import Login_user_form
from forms.Shop_registration_form import Shop_registration
from data.models.users import User
from data.models.shops import Shop
from data.tests.shop_creation_tests import shop_creation_test

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
api = Api(app)
app.config['SECRET_KEY'] = 'MARKETPLACE_SECRET_KEY'


@app.route('/')
def main_menu():
    return render_template('base.html')


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/register', methods=['POST', 'GET'])
def register_user():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация', form=form, message='Пароли не совпадают')
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пользователь с такой почтой уже зарегистрирован")
        user = User()
        user.email = form.email.data
        user.name = form.name.data
        user.surname = form.surname.data
        user.address = form.address.data
        user.phone_number = form.phone_number.data
        user.email = form.email.data
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['POST', 'GET'])
def Login_user():
    form = Login_user_form()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect('/')
        return render_template('login_user.html', form=form, message='Неправильный адрес электронной почты или пароль')

    return render_template('login_user.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')


@login_required
@app.route('/create_shop', methods=['GET', 'POST'])
def create_shop():
    form = Shop_registration()
    if form.validate_on_submit():
        if not shop_creation_test(form):
            return render_template('shop_registration.html', form=form, message="Магазин с таким названием существует")
        f = form.logo.data
        filename = secure_filename(f.filename)
        if filename in os.listdir('static/photo'):
            return render_template('shop_registration.html', form=form, message="Лого с таким названием существует: смените название файла логотипа")
        f.save(os.path.join('static', 'photo', filename))
        shop = Shop(
            name=form.name.data,
            owner_id=current_user.id,
            description=form.description.data,
            logo_url=filename
        )
        db_sess = db_session.create_session()
        db_sess.add(shop)
        db_sess.commit()
        return redirect('/')

    return render_template('shop_registration.html', form=form)


@login_required
@app.route('/my_shops')
def my_shops():
    db_sess = db_session.create_session()
    shops = db_sess.query(Shop).filter(Shop.owner_id == current_user.id).all()
    return render_template('my_shops.html', shops=shops)


@login_required
@app.route('/shop/<int:shop_id>')
def shop(shop_id):
    db_sess = db_session.create_session()
    shop = db_sess.query(Shop).filter(Shop.id == shop_id).first()
    if shop:
        return render_template('shop.html', shop=shop)


@login_required
@app.route('/edit_shop/<int:shop_id>', methods=['GET', 'POST'])
def edit_shop(shop_id):
    form = Shop_registration()
    if request.method == 'GET':
        db_sess = db_session.create_session()
        shop = db_sess.query(Shop).filter(Shop.id == shop_id).first()
        if shop:
            form.name.data = shop.name
            form.description.data = shop.description
            form.submit.label.text = 'Изменить'
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        shop = db_sess.query(Shop).filter(Shop.id == shop_id, Shop.user == current_user).first()
        if shop:
            shop.name = form.name.data
            shop.description = form.description.data
            f = form.logo.data
            if f:
                os.remove(f'./static/photo/{shop.logo_url}')
                filename = secure_filename(f.filename)
                f.save(os.path.join('static', 'photo', filename))
                shop.logo_url = filename
            db_sess.commit()
            return redirect(f'/shop/{shop_id}')
        else:
            abort(404)
    return render_template('shop_registration.html', form=form)

@login_required
@app.route('/delete_shop/<int:shop_id>')
def delete_shop(shop_id):
    db_sess = db_session.create_session()
    shop = db_sess.query(Shop).filter(Shop.id == shop_id, Shop.user == current_user).first()
    if shop:
        os.remove(f'./static/photo/{shop.logo_url}')
        db_sess.delete(shop)
        db_sess.commit()
        return redirect('/my_shops')
    abort(404)


def main():
    db_session.global_init('db/market.db')
    app.run(host='127.0.0.1', port=8080)


if __name__ == '__main__':
    main()
