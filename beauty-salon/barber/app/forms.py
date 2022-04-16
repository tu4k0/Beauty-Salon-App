import wtforms as f

import flask_wtf as ft


class LoginForm(ft.FlaskForm):
    login = f.StringField('Логин', [f.validators.DataRequired()])
    password = f.StringField('Пароль', [f.validators.DataRequired(), f.validators.Length(min=8, max=30)])
    submit = f.SubmitField('Войти')


class RegisterForm(ft.FlaskForm):
    login = f.StringField('Логин', [f.validators.DataRequired()])
    password = f.StringField('Пароль', [f.validators.DataRequired(), f.validators.Length(min=8, max=30)])
    submit = f.SubmitField('Зарегестрироваться')


class OrderForm(ft.FlaskForm):
    payment_type = f.SelectField('Тип оплаты',choices=['Наличные', 'Карта'])
    name = f.StringField('Имя', [f.validators.Length(min=1, max=20)])
    last_name = f.StringField('Фамилия', [f.validators.Length(min=1, max=20)])
    surname = f.StringField('Отчество', [f.validators.Length(min=1, max=20)])
    phone = f.StringField('Телефон')
    time = f.DateTimeField('Дата проведения', render_kw={'placeholder': 'гггг-мм-дд чч:мм:сс'})
    submit = f.SubmitField('Сделать заказ')


class StatusForm(ft.FlaskForm):
    status = f.SelectField('Статус', choices=[(1, 'Cозданный'), (2, 'В реализации'), (3, 'Отклонен'), (4, 'Завершен'), (5, 'Оплачен')])
    submit = f.SubmitField('Изменить статус')
