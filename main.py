from flask import Flask, render_template
from flask_restful import Api

app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = 'MARKETPLACE_SECRET_KEY'


@app.route('/')
def main_menu():
    return render_template('base.html')


def main():
    app.run(host='127.0.0.1', port=8080)


if __name__ == '__main__':
    main()
