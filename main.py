import os
import random
from data.mail_sender import send_email
from flask import Flask, render_template, redirect, request, abort, jsonify, flash
from flask_restful import Api
from sqlalchemy.orm.attributes import flag_modified
from werkzeug.utils import secure_filename

from data import db_session
from flask_login import login_user, logout_user, LoginManager, login_required, current_user
from forms.RegisterForm import RegisterForm
from forms.Login_user_form import Login_user_form
from forms.Shop_registration_form import Shop_registration
from forms.product_creating_form import ProductForm
from data.models.users import User
from data.models.shops import Shop
from data.models.products import Product
from data.models.shopping_cart import Shopping_cart
from data.tests.shop_creation_tests import shop_creation_test
from data.tests.product_edit_test import product_edit_test
from data.tests.product_delete_test import product_delete_test

from data.api.products_resource import ProductsResource, ProductsListResource
from data.api.shops_resources import ShopsResource, ShopsListResource

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
api = Api(app)
app.config['SECRET_KEY'] = 'MARKETPLACE_SECRET_KEY'

@app.route('/catalog')
@app.route('/')
def catalog():
    db_sess = db_session.create_session()
    products = db_sess.query(Product).all()
    return render_template('catalog.html', products=products)




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

        cart = Shopping_cart(
            user_id=user.id
        )
        db_sess.add(cart)
        db_sess.commit()
        return redirect('/login')
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
@app.route('/edit_user', methods=['GET', 'POST'])
def edit_user():
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(current_user.id)
    if not user:
        abort(404)
    form = RegisterForm()
    if request.method == 'GET':
        form.name.data = user.name
        form.surname.data = user.surname
        form.address.data = user.address
        form.phone_number.data = user.phone_number
        form.email.data = user.email
        form.submit.label.text = 'Изменить'
    if form.validate_on_submit():
        user.name = form.name.data
        user.surname = form.surname.data
        user.address = form.address.data
        user.phone_number = form.phone_number.data
        user.email = form.email.data
        user.set_password(form.password.data)
        db_sess.commit()
        login_user(user)
        return redirect('/')
    return render_template('register.html', form=form)




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
            return render_template('shop_registration.html', form=form,
                                   message="Лого с таким названием существует: смените название файла логотипа")
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
    products = db_sess.query(Product).filter(Product.shop_id == shop_id).all()
    if shop:
        return render_template('shop.html', shop=shop, products=products)


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


@login_required
@app.route('/create_product/<int:shop_id>', methods=['GET', 'POST'])
def create_product(shop_id):
    db_sess = db_session.create_session()
    shop = db_sess.query(Shop).get(shop_id)
    if not shop:
        abort(404)
    if shop.user != current_user:
        abort(403)
    form = ProductForm()
    if form.validate_on_submit():
        f = form.logo.data
        if not f:
            return render_template('product_creating.html', form=form,
                                   message="No file was supplied. Please upload a valid file.")
        filename = secure_filename(f.filename)
        if filename in os.listdir('static/photo'):
            return render_template('product_creating.html', form=form,
                                   message="Файл с таким именем уже существует: измените название файла")
        f.save(os.path.join('static', 'photo', filename))
        product = Product(
            shop_id=shop.id,
            category=form.category.data,
            name=form.name.data,
            description=form.description.data,
            price=form.price.data,
            logo_url=filename,
            stock_quantity=form.stock_quantity.data
        )
        db_sess.add(product)
        db_sess.commit()
        return redirect(f'/product/{product.id}')
    return render_template('product_creating.html', form=form)


@login_required
@app.route('/edit_product/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    db_sess = db_session.create_session()
    product = db_sess.query(Product).get(product_id)
    if not product:
        abort(404)
    shop = db_sess.query(Shop).get(product.shop_id)
    if not shop or shop.user != current_user:
        abort(403)
    form = ProductForm()
    if request.method == 'GET':
        # Заполнение формы текущими данными товара
        form.name.data = product.name
        form.description.data = product.description
        form.price.data = product.price
        form.stock_quantity.data = product.stock_quantity
        form.category.data = product.category
        form.submit.label.text = 'Изменить'
    if form.validate_on_submit():
        # Обновление данных товара
        product.name = form.name.data
        product.description = form.description.data
        product.price = form.price.data
        product.stock_quantity = form.stock_quantity.data
        product.category = form.category.data
        f = form.logo.data
        if f:
            if product.logo_url and os.path.exists(f'./static/photo/{product.logo_url}'):
                os.remove(f'./static/photo/{product.logo_url}')
            filename = secure_filename(f.filename)
            if filename in os.listdir('static/photo'):
                flash("Файл с таким именем уже существует. Переименуйте загружаемый файл", "warning")
                return render_template('product_edit.html', form=form, product=product)
            f.save(os.path.join('static', 'photo', filename))
            product.logo_url = filename
        db_sess.commit()
        product_edit_test(product)
        return redirect(f'/product/{product_id}')
    return render_template('product_creating.html', form=form, product=product)


@login_required
@app.route('/delete_product/<int:product_id>')
def delete_product(product_id):
    db_sess = db_session.create_session()
    product = db_sess.query(Product).get(product_id)
    if product:
        if product.shop.user != current_user:
            abort(403)
        product_delete_test(product.id)
        os.remove(f'./static/photo/{product.logo_url}')
        db_sess.delete(product)
        db_sess.commit()
        db_sess.close()
        return redirect('/catalog')
    abort(404)


@app.route('/product/<int:product_id>')
def product(product_id):
    db_sess = db_session.create_session()
    product = db_sess.query(Product).get(product_id)
    if product:
        return render_template('product.html', product=product)
    abort(404)


@login_required
@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    db_sess = db_session.create_session()
    cart = db_sess.query(Shopping_cart).filter(Shopping_cart.user_id == current_user.id).first()
    product = db_sess.query(Product).get(product_id)
    if not cart:
        cart = Shopping_cart(user_id=current_user.id, data=[])
        cart.data.append({'product_id': product_id, 'quantity': 1, 'price': product.price})
        db_sess.add(cart)
    else:
        if product_id in [item['product_id'] for item in cart.data]:
            for item in cart.data:
                if item['product_id'] == product_id:
                    item['quantity'] += 1
                    break
        else:
            cart.data.append({'product_id': product_id, 'quantity': 1, 'price': product.price})
    db_sess.commit()
    return redirect('/cart')


@login_required
@app.route('/cart')
def cart():
    db_sess = db_session.create_session()
    if not current_user.is_authenticated:
        abort(403)
    cart = db_sess.query(Shopping_cart).filter(Shopping_cart.user_id == current_user.id).first()
    if not cart:
        cart = Shopping_cart(user_id=current_user.id,
                             data=[])
    final_sum = 0

    for js in cart.data:
        product = db_sess.query(Product).get(js['product_id'])
        js['name'] = product.name
        js['logo_url'] = f'/static/photo/{product.logo_url}'
        final_sum += js['price'] * js['quantity']
    return render_template('cart.html', products=cart.data, final_sum=final_sum)


@login_required
@app.route('/cart/remove', methods=['GET', 'POST'])
def remove_from_cart():
    product_id = request.form.get('product_id')
    db_sess = db_session.create_session()
    cart = db_sess.query(Shopping_cart).filter(Shopping_cart.user_id == current_user.id).first()
    for js in cart.data:
        if js['product_id'] == int(product_id):
            cart.data.remove(js)
            break
    db_sess.commit()
    return redirect('/cart')


@login_required
@app.route('/cart/update', methods=['GET', 'POST'])
def update_cart():
    product_id = int(request.form.get('product_id'))
    quantity = int(request.form.get('quantity'))
    db_sess = db_session.create_session()
    max_q = db_sess.query(Product).get(product_id).stock_quantity
    cart = db_sess.query(Shopping_cart).filter(Shopping_cart.user_id == current_user.id).first()
    for elem in cart.data:
        if product_id == elem['product_id']:
            if quantity > max_q:
                flash(f'Превышено количество товара: в наличии {max_q}', 'warning')
                return redirect('/cart')
            elem['quantity'] = quantity
    flag_modified(cart, "data")
    db_sess.commit()
    db_sess.close()
    return redirect('/cart')


@login_required
@app.route('/checkout')
def checkout():
    db_sess = db_session.create_session()
    cart = db_sess.query(Shopping_cart).filter(Shopping_cart.user_id == current_user.id).first()
    users = {}
    if cart:
        for js in cart.data:
            product = db_sess.query(Product).get(js['product_id'])
            shop = db_sess.query(Shop).get(product.shop_id)
            user = shop.user
            email = user.email
            if email not in users:
                users[email] = [
                    {'name': product.name, 'id': product.id, 'quantity': js['quantity'], 'price': js['price']}]
            else:
                users[email].append(
                    {'name': product.name, 'id': product.id, 'quantity': js['quantity'], 'price': js['price']})
        for email in users:
            if send_email(email, "Пришел заказ", users[email], current_user):
                print("Email was sent")
                for elem in users[email]:
                    product = db_sess.query(Product).get(elem['id'])
                    product.stock_quantity -= elem['quantity']
                    flag_modified(product, 'stock_quantity')
                    db_sess.commit()
            else:
                print("Email was not sent")
                flash(
                    "Произошла внутренняя ошибка, заказ не был оформлен. Обратитесь в техническую поддержку.",
                    "danger")
                return redirect('/cart')
    db_sess.delete(cart)
    db_sess.commit()
    db_sess.close()
    flash(
        "Ваш заказ успешно оформлен. Ожидайте, пока с вами свяжутся представители магазина. Если этого не произойдет, "
        "проверьте данные для связи в профиле и повторите заказ.", "success")
    return redirect('/cart')


def main():
    db_session.global_init('db/market.db')
    api.add_resource(ProductsResource, '/api/products/<int:product_id>')
    api.add_resource(ProductsListResource, '/api/products')
    api.add_resource(ShopsResource, '/api/shops/<int:shop_id>')
    api.add_resource(ShopsListResource, '/api/shops')
    app.run(host='127.0.0.1', port=8080)


if __name__ == '__main__':
    main()
