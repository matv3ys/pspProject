import time
from random import randint
import uuid
import os
import zipfile

from flask import Flask, render_template, url_for, redirect, request, abort, session, flash
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from sqlalchemy.sql.functions import register_function
from sqlalchemy.testing import db_spec, startswith_

from forms import LoginForm, RegisterForm, RegisterConfForm, CreateGroupForm, CreateTaskForm, CreateContestForm
from database import session_factory
from models import UserTable, GroupTable, UserGroupTable, TestTable, TaskTable, ContestTable
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

@app.route('/tasks', methods=['GET', 'POST'])
def tasks():
    if not (current_user.is_authenticated and current_user.is_organizer):
        return redirect('/')

    db_session = session_factory()

    tasks = db_session.query(TaskTable).all()

    user_tasks = [task for task in tasks if task.author_id == current_user.user_id]
    other_tasks = [task for task in tasks if task.author_id != current_user.user_id]

    return render_template("tasks.html", user_tasks=user_tasks,
                           other_tasks=other_tasks, title='Задачи')


@app.route('/create_task', methods=['GET', 'POST'])
@login_required
def create_task():
    """ обработчик создания группы """

    if not (current_user.is_authenticated and current_user.is_organizer):
        return redirect('/')

    form = CreateTaskForm()
    if form.validate_on_submit():
        f = form.tests.data
        filename = str(uuid.uuid4())
        fpath = os.path.join('static', 'tmp', filename)
        f.save(fpath)

        with zipfile.ZipFile(fpath, "r") as zf:
            names = zf.namelist()
            if len(names) % 2 != 0:
                os.remove(fpath)
                return render_template('create_task.html', title='Создать задачу',
                                       form=form, message="Ошибка: нечетное количество файлов в архиве")

            tests = []
            q_of_tests = len(names) // 2
            for i in range(1, q_of_tests + 1):
                in_name = f"in_{i}.txt"
                out_name = f"out_{i}.txt"
                if in_name not in names:
                    os.remove(fpath)
                    return render_template('create_task.html', title='Создать задачу',
                                           form=form, message=f"Ошибка: отсутствует файл {in_name}")
                if out_name not in names:
                    os.remove(fpath)
                    return render_template('create_task.html', title='Создать задачу',
                                           form=form, message=f"Ошибка: отсутствует файл {out_name}")

                in_data = zf.read(in_name).decode("utf-8").strip()
                out_data = zf.read(out_name).decode("utf-8").strip()
                tests.append((i, in_data, out_data))

        os.remove(fpath)

        db_session = session_factory()

        task = TaskTable(
            title=form.title.data,
            time_limit=form.time_limit.data,
            description=form.description.data,
            input_info=form.input_info.data,
            output_info=form.output_info.data,
            author_id=current_user.user_id
        )

        # https: // stackoverflow.com / questions / 1316952 / sqlalchemy - flush - and -get - inserted - id
        db_session.add(task)
        db_session.flush()
        db_session.refresh(task)

        task_id = task.task_id

        for test_tup in tests:
            test = TestTable(
                task_id=task_id,
                test_num=test_tup[0],
                input_data=test_tup[1],
                output_data=test_tup[2],
                is_open=False
            )
            db_session.add(test)

        db_session.commit()

        return redirect("/tasks")

    return render_template('create_task.html', title='Создать задачу', form=form)


@app.route('/task', methods=['GET', 'POST'])
def task():
    task_id = int(request.args.get("task_id"))

    if not (current_user.is_authenticated and current_user.is_organizer):
        return redirect('/')

    db_session = session_factory()

    task = db_session.query(TaskTable).where(TaskTable.task_id == task_id).first()
    if not task:
        abort(404)

    tests = db_session.query(TestTable).where((TestTable.task_id == task_id) & (TestTable.is_open == True)).all()

    return render_template('task.html', title=task.title, task=task, tests=tests,
                           css=url_for('static', filename='css/task_style.css'))

@app.route('/edit_task/<int:task_id>', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    action = request.args.get("action")
    test_id = request.args.get("test_id")

    if not (current_user.is_authenticated and current_user.is_organizer):
        return redirect('/')

    form = CreateTaskForm()

    db_session = session_factory()

    task = db_session.query(TaskTable).where(TaskTable.task_id == task_id).first()
    if task is None:
        abort(404)
    elif task.author_id != current_user.user_id:
        abort(403)


    if form.is_submitted():
        task.title = form.title.data
        task.time_limit = form.time_limit.data
        task.description = form.description.data
        task.input_info = form.input_info.data
        task.output_info = form.output_info.data
    else:
        form.title.data = task.title
        form.time_limit.data = task.time_limit
        form.description.data = task.description
        form.input_info.data = task.input_info
        form.output_info.data = task.output_info
        form.submit.label.text = "Сохранить изменения"

    if action == "hide" and test_id is not None:
        test_id = int(test_id)
        test = db_session.query(TestTable).where(TestTable.test_id == test_id).first()
        if test is not None:
            test.is_open = False
    elif action == "show" and test_id is not None:
        test_id = int(test_id)
        test = db_session.query(TestTable).where(TestTable.test_id == test_id).first()
        if test is not None:
            test.is_open = True

    db_session.flush()


    opened_tests = db_session.query(TestTable).where(
        (TestTable.task_id == task_id) & (TestTable.is_open == True)
    ).all()
    opened_tests.sort(key=lambda x: x.test_num)
    closed_tests = db_session.query(TestTable).where(
        (TestTable.task_id == task_id) & (TestTable.is_open == False)
    ).all()
    closed_tests.sort(key=lambda x: x.test_num)

    db_session.commit()

    return render_template('edit_task.html', title='Редактирование задачи',
                           form=form, opened_tests=opened_tests, closed_tests=closed_tests,
                           css=url_for('static', filename='css/edit_task_style.css'))

@app.route('/contests', methods=['GET'])
def contests():
    if not current_user.is_authenticated:
        return redirect('/')

    db_session = session_factory()
    if current_user.is_organizer:
        user_contests = db_session.query(
            ContestTable
        ).where(
            ContestTable.author_id == current_user.user_id
        ).all()
    else:
        user_contests = []
    print()



    # user_id = session["user_id"]
    # db_session = session_factory()
    #
    # groups = db_session.query(
    #     GroupTable.group_id,
    #     GroupTable.group_name,
    #     UserGroupTable.status,
    #     GroupTable.owner_id,
    #     UserTable.name,
    #     UserTable.surname
    # ).join(
    #     UserGroupTable,
    #     (GroupTable.group_id == UserGroupTable.group_id) & (UserGroupTable.user_id == current_user.user_id),
    #     isouter=True
    # ).join(
    #     UserTable,
    #     GroupTable.owner_id == UserTable.user_id,
    #     isouter=True
    # ).all()
    #
    # user_groups = [GroupInfo(i) for i in groups if i[2] == 2 or i[3] == current_user.user_id]
    # other_groups = [GroupInfo(i) for i in groups if i[2] != 2]

    return render_template("contests.html", user_contests=user_contests,
                           other_contests=[], title='Контесты')

@app.route('/create_contest', methods=['GET', 'POST'])
def create_contest():
    """ обработчик создания контеста """

    if not (current_user.is_authenticated and current_user.is_organizer):
        return redirect('/')

    form = CreateContestForm()
    if form.validate_on_submit():
        with session_factory() as db_session:
            if form.start_time.data >= form.end_time.data:
                return render_template('create_contest.html',
                                       title='Создать контест',
                                       form=form,
                                       message="Ошибка: время начала >= время окончания")

            contest = ContestTable(
                name=form.name.data,
                description=form.description.data,
                author_id=current_user.user_id,
                start_time=form.start_time.data,
                end_time=form.end_time.data
            )

            db_session.add(contest)
            db_session.commit()
        return redirect("/contests")

    return render_template('create_contest.html', title='Создать контест', form=form)




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