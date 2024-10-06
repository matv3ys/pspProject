import time
from random import randint

from flask import Flask, render_template, url_for, redirect, request, abort, session, flash
from flask_login import current_user
from forms import LoginForm, RegisterForm, RegisterConfForm
from database import session_factory
from models import UserTable
from werkzeug.security import generate_password_hash

from utils import send_code_email

app = Flask(__name__)
app.config['SECRET_KEY'] = "kek"

def main():
    app.run(port=8080, host='127.0.0.1')

@app.route('/')
def main_page():
    """ обработчик главной страницы """

    return render_template('home.html', title='PrivetMIR',
                           css=url_for('static', filename='css/home_style.css'))


@app.route('/join', methods=['GET', 'POST'])
def join():
    """ обработчик регистрации пользователя """
    # if current_user.is_authenticated:
    #     return redirect('/profile')

    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('join.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        # session = db_session.create_session()
        with session_factory() as db_session:
            if db_session.query(UserTable).filter(UserTable.login == form.login.data).first():
                return render_template('join.html', title='Регистрация',
                                       form=form,
                                       message="Введенный логин занят",)

        code = randint(100000, 999999)

        session["confirm_data"] = {
            "login": form.login.data,
            "email": form.email.data,
            "surname": form.surname.data,
            "name": form.name.data,
            "hashed_password": generate_password_hash(form.password.data),
            "code": code
        }
        print(code)
        #send_code_email(code, form.email.data)

        return redirect('/confirm_email')
    return render_template('join.html', title='Регистрация', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    return render_template('login.html', title='Авторизация', form=form)

@app.route('/confirm_email', methods=['GET', 'POST'])
def confirm_email():
    referrer = request.referrer
    if referrer is None or not (referrer.endswith("/join") or
                                referrer.endswith("/confirm_email") or
                                referrer.endswith("/resend_conf_code")):
        return redirect("/")

    form = RegisterConfForm()

    if form.validate_on_submit():
        confirm_data = session.get("confirm_data", None)
        if confirm_data is None:
            return redirect("/")
        code = confirm_data["code"]

        if form.code.data != code:
            return render_template('register_conf.html', title="Подтверждение регистрации",
                                   form=form,
                                   message="Неверный код, попробуйте еще раз")

        user = UserTable(
            login=confirm_data["login"],
            email=confirm_data["email"],
            surname=confirm_data["surname"],
            name=confirm_data["name"],
            hashed_password=confirm_data["hashed_password"]
        )
        with session_factory() as db_session:
            db_session.add(user)
            db_session.commit()
        return redirect("/login")

    return render_template("register_conf.html", title="Подтверждение регистрации", form=form)

@app.route('/resend_conf_code', methods=['GET'])
def resend_conf_code():
    referrer = request.referrer
    if referrer is None or not referrer.endswith("/confirm_email"):
        return redirect("/")
    conf_data = session.get("confirm_data", None)
    if conf_data is None:
        return redirect("/")
    code = randint(100000, 999999)
    conf_data["code"] = code
    print(code)
    #send_code_email(code, form.email.data)
    session["confirm_data"] = conf_data
    return redirect("/confirm_email")


if __name__ == "__main__":
    main()