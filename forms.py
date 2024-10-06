from flask_wtf import FlaskForm
from wtforms import BooleanField, FileField, EmailField, StringField
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

    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')