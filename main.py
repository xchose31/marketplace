from flask import Flask, render_template, redirect
from flask_restful import Api
from data import db_session
from flask_login import login_user, login_required, logout_user, current_user, LoginManager
from forms.RegisterForm import RegisterForm
from forms.Login_user_form import Login_user_form
from data.users import User

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


def main():
    db_session.global_init('db/market.db')
    app.run(host='127.0.0.1', port=8080)


if __name__ == '__main__':
    main()
