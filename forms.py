from flask_wtf import FlaskForm
from wtforms import BooleanField, FileField, EmailField, StringField, IntegerField, TextAreaField
from wtforms import PasswordField, SubmitField
from wtforms.fields.numeric import IntegerField
from wtforms.validators import DataRequired, Email

class RegisterForm(FlaskForm):
    """ форма регистрации """

    email = EmailField('E-mail:', validators=[DataRequired("Введите email"), Email("Некорректный email")])
    login = StringField("Логин:", validators=[DataRequired("Введите логин")])
    password = PasswordField('Пароль:', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль:', validators=[DataRequired()])
    surname = StringField('Фамилия:', validators=[DataRequired()])
    name = StringField('Имя:', validators=[DataRequired()])
    agree = BooleanField('Согласен на обработку персональных данных:',
                         validators=[DataRequired("Необходимо ваше согласие")])
    #avatar = FileField('Загрузите фото профиля')
    submit = SubmitField('Зарегистрироваться')

class RegisterConfForm(FlaskForm):
    """ форма подтверждения регистрации """

    code = IntegerField('Код подтверждения:', validators=[DataRequired("Введите код")])
    submit = SubmitField('Подтвердить регистрацию')

class LoginForm(FlaskForm):
    """ форма входа на сайт """

    login = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')

class CreateGroupForm(FlaskForm):
    """ форма подтверждения регистрации """

    name = StringField('Имя группы', validators=[DataRequired("Введите название группы")])
    submit = SubmitField('Создать группу')


class CreateTaskForm(FlaskForm):
    """ форма создания задачи """

    title = StringField('Название задачи', validators=[DataRequired("Введите название задачи")])
    time_limit = IntegerField('Ограничение по времени (мс)',
                              validators=[DataRequired("Введите ограничение по времени в миллисекундах")])
    description = TextAreaField('Условие задачи', validators=[DataRequired("Введите условие задачи")])
    input_info = TextAreaField('Ожидаемый ввод', validators=[DataRequired("Введите ожидаемые входные данные")])
    output_info = TextAreaField('Ожидаемый вывод', validators=[DataRequired("Введите ожидаемые выходные данные")])
    tests = FileField("Тесты", validators=[DataRequired("Загрузите .zip архив с тестами")])
    submit = SubmitField('Создать задачу')