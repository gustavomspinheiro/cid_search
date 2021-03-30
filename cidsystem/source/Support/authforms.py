import email_validator

from flask_wtf import FlaskForm
from wtforms import Form, StringField, PasswordField, SubmitField, BooleanField, validators
from wtforms.validators import Email, Length, DataRequired, EqualTo, ValidationError

from cidsystem.source.Models.user import User

class RegistrationForm(FlaskForm):
    adminName = StringField('Nome', validators=[DataRequired(message='Campo requerido'), Length(min=3, max=30, message='O nome precisa ter entre %(min)d e %(max)d caracteres')], render_kw={'placeholder': 'Nome:'})
    adminSurname = StringField('Sobrenome', validators=[DataRequired(message='Campo requerido'), Length(min=3, max=30, message='O sobrenome precisa ter entre %(min)d e %(max)d caracteres')], render_kw={'placeholder': 'Sobrenome:'})
    adminEmail = StringField('Email', validators=[DataRequired(message='Campo requerido'), Email(message='O e-mail precisa ser válido')],render_kw={'placeholder': 'E-mail:'})
    adminPass = PasswordField('Senha', validators=[DataRequired(message='Campo requerido'), Length(min=6, max = 20, message='Erro. tente outra senha')], render_kw={'placeholder': 'Senha:'})
    confirmPass = PasswordField('Confirme a Senha', validators=[DataRequired(message='Campo requerido'), EqualTo('adminPass', message='A confirmação de senha precisa ser igual a original')], render_kw={'placeholder': 'Confirmação da senha:'})
    submit = SubmitField('Cadastrar')

    def validateByEmail(self, email):
        user = User.query.filter_by(email=email).first()
        if user:
            return False
        return True

class LoginForm(FlaskForm):
    adminEmail = StringField('Email', validators=[DataRequired(), Email()], render_kw={'placeholder': 'E-mail:'})
    adminPass = PasswordField('Senha', validators=[DataRequired(), Length(min=6, max = 20)], render_kw={'placeholder': 'Senha:'})
    remember = BooleanField('Lembrar-me')
    submit = SubmitField('Login')
