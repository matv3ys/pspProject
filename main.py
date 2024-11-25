import time
from random import randint

from flask import Flask, render_template, url_for, redirect, request, abort, session, flash
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from sqlalchemy.sql.functions import register_function

from forms import LoginForm, RegisterForm, RegisterConfForm, CreateGroupForm
from database import session_factory
from models import UserTable, GroupTable, UserGroupTable
from werkzeug.security import generate_password_hash

from utils import send_code_email

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = "kek"

class GroupInfo():
    group_id: int
    group_name: str
    status: int
    owner_id: int
    owner_name: str
    owner_surname: str

    def __init__(self, item):
        self.group_id = item[0]
        self.group_name = item[1]
        self.status = item[2]
        self.owner_id = item[3]
        self.owner_name = item[4]
        self.owner_surname = item[5]

class UserInfo():
    surname: str
    name: str
    login: str
    user_id: int

    def __init__(self, item):
        self.surname = item[1]
        self.name = item[2]
        self.login = item[3]
        self.user_id = item[4]


def main():
    app.run(port=8080, host='127.0.0.1')

@app.route('/')
def main_page():
    """ обработчик главной страницы """

    return render_template('home.html', title='PrivetMIR',
                           css=url_for('static', filename='css/home_style.css'))

@app.route('/groups', methods=['GET', 'POST'])
def groups():
    '''
        1 - requested
        2 - participant
    '''

    if not current_user.is_authenticated:
        return redirect('/')
    user_id = session["user_id"]
    db_session = session_factory()

    groups = db_session.query(
        GroupTable.group_id,
        GroupTable.group_name,
        UserGroupTable.status,
        GroupTable.owner_id,
        UserTable.name,
        UserTable.surname
    ).join(
        UserGroupTable,
        (GroupTable.group_id == UserGroupTable.group_id) & (UserGroupTable.user_id == current_user.user_id),
        isouter=True
    ).join(
        UserTable,
        GroupTable.owner_id == UserTable.user_id,
        isouter=True
    ).all()

    user_groups = [GroupInfo(i) for i in groups if i[2] == 2 or i[3] == current_user.user_id]
    other_groups = [GroupInfo(i) for i in groups if i[2] != 2]

    return render_template("groups.html", user_g=user_groups,
                           other_g=other_groups, title='Группы')

@app.route('/group_button', methods=['GET', 'POST'])
def group_button():
    action = request.args.get("action")
    group_id = request.args.get("group_id")
    if action == "leave":
        with session_factory() as db_session:
            row = db_session.query(UserGroupTable).filter(
                UserGroupTable.group_id == int(group_id),
                UserGroupTable.user_id == current_user.user_id
            ).first()
            if row and row.status == 2:
                db_session.delete(row)
                db_session.commit()
    elif action == "join":
        with session_factory() as db_session:
            row = db_session.query(UserGroupTable).filter(
                UserGroupTable.group_id == int(group_id),
                UserGroupTable.user_id == current_user.user_id
            ).first()
            if not row:
                row = UserGroupTable(user_id=current_user.user_id, group_id=group_id, status=1)
                db_session.add(row)
                db_session.commit()


    return redirect("/groups")


@app.route('/create_group', methods=['GET', 'POST'])
def create_group():
    """ обработчик создания группы """

    if not (current_user.is_authenticated and current_user.is_organizer):
        return redirect('/')

    form = CreateGroupForm()
    if form.validate_on_submit():
        with session_factory() as db_session:
            if db_session.query(GroupTable).filter(GroupTable.group_name == form.name.data).first():
                return render_template('create_group.html', title='Создать группу',
                                       form=form,
                                       message="Имя группы занято",)

            group = GroupTable(
                group_name=form.name.data,
                owner_id=current_user.user_id
            )

            db_session.add(group)
            db_session.commit()
        return redirect("/groups")

    return render_template('create_group.html', title='Создать группу', form=form)

@app.route('/manage_group', methods=['GET', 'POST'])
def manage_group():
    group_id = int(request.args.get("group_id"))
    group_name = request.args.get("group_name")

    if not current_user.is_authenticated:
        return redirect('/')

    with session_factory() as db_session:
        owner_id = db_session.query(GroupTable.owner_id).where(GroupTable.group_id == group_id).first()
        if owner_id is None or owner_id[0] != current_user.user_id:
            abort(403)

    db_session = session_factory()

    users = (db_session.query(
        UserGroupTable.status,
        UserTable.surname,
        UserTable.name,
        UserTable.login,
        UserTable.user_id
    ).join(
        UserTable,
        UserTable.user_id == UserGroupTable.user_id,
        isouter=True
    ).filter(
        UserGroupTable.group_id == group_id
    ).all())

    member_reqs = [UserInfo(i) for i in users if i[0] == 1]
    members = [UserInfo(i) for i in users if i[0] == 2]

    return render_template('manage_group.html', group_name=group_name,
                           group_id=group_id, member_reqs=member_reqs,
                           members=members, title='Управление группой')

@app.route('/manage_group_button', methods=['GET', 'POST'])
def manage_group_button():
    group_name = request.args.get("group_name")
    group_id = int(request.args.get("group_id"))
    user_id = int(request.args.get("user_id"))
    action = request.args.get("action")

    if not current_user.is_authenticated:
        return redirect('/')

    with session_factory() as db_session:
        owner_id = db_session.query(GroupTable.owner_id).where(GroupTable.group_id == group_id).first()
        if owner_id is None or owner_id[0] != current_user.user_id:
            abort(403)

    db_session = session_factory()
    u_g_row = db_session.query(
        UserGroupTable
    ).where(
        (UserGroupTable.user_id == user_id) & (UserGroupTable.group_id == group_id)
    ).first()

    if u_g_row is None:
        abort(403)

    if action == 'accept' and u_g_row.status == 1:
        u_g_row.status = 2
        db_session.commit()
    elif action == 'reject' and u_g_row.status == 1 or \
         action == 'exclude' and u_g_row.status == 2:
        db_session.delete(u_g_row)
        db_session.commit()
    else:
        abort(403)

    return redirect(f"/manage_group?group_name={group_name}&group_id={group_id}")



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
        send_code_email(code, form.email.data)

        return redirect('/confirm_email')
    return render_template('join.html', title='Регистрация', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect('/')

    form = LoginForm()
    if form.validate_on_submit():
        with session_factory() as db_session:
            user = db_session.query(UserTable).filter(UserTable.login == form.login.data).first()
            if user and user.check_password(form.password.data):
                session["user_id"] = user.user_id
                login_user(user, remember=form.remember_me.data)
                return redirect("/")
        return render_template('login.html', title='Авторизация',
                               message="Неправильный логин или пароль",
                               form=form)

    return render_template('login.html', title='Авторизация', form=form)

@app.route('/confirm_email', methods=['GET', 'POST'])
def confirm_email():
    referrer = request.referrer
    if referrer is None or not (referrer.endswith("/join") or
                                referrer.endswith("/confirm_email") or
                                referrer.endswith("/resend_conf_code")):
        return redirect("/")

    message = None
    if referrer.endswith("/confirm_email"):
        message = session.get("message")

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
            is_organizer=False,
            hashed_password=confirm_data["hashed_password"]
        )
        with session_factory() as db_session:
            db_session.add(user)
            db_session.commit()
        return redirect("/login")

    if message is None:
        message=''
    return render_template("register_conf.html", title="Подтверждение регистрации",
                           form=form, message=message)

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
    send_code_email(code, conf_data["email"])
    session["confirm_data"] = conf_data
    session["message"] = "Новый код выслан"
    return redirect("/confirm_email")

@login_manager.user_loader
def load_user(user_id):
    """ обработчик входа пользователя """

    session = session_factory()
    return session.query(UserTable).get(user_id)

@app.route('/logout')
@login_required
def logout():
    """ обработчик выхода пользователя """

    logout_user()
    return redirect("/")


if __name__ == "__main__":
    main()