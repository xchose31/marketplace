from flask import Flask, render_template, redirect
from flask_restful import Api
from data import db_session
from forms.RegisterForm import RegisterForm
from data.users import User

app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = 'MARKETPLACE_SECRET_KEY'


@app.route('/')
def main_menu():
    return render_template('base.html')


@app.route('/register', methods=['POST', 'GET'])
def register():
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


def main():
    db_session.global_init('db/market.db')
    app.run(host='127.0.0.1', port=8080)


if __name__ == '__main__':
    main()
