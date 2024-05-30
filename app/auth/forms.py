from flask_wtf import FlaskForm
from flask_wtf.form import _Auto
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length
from app.models import User
from flask_babel import _, lazy_gettext as _l
import re

class LoginForm(FlaskForm):
    username = StringField(_l('Username'), validators=[DataRequired()])
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    remember_me = BooleanField(_l('Remember Me?'))
    submit = SubmitField(_l('Log in'))


class RegistrationForm(FlaskForm):
    username = StringField(_l('Username'), validators=[DataRequired()])
    email = StringField(_l('Email'), validators=[DataRequired(), Email()])
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    confirm_password = PasswordField(
        _l('Confirm Password'), validators=[EqualTo('password', message='Passwords must match!!'), DataRequired()]) 
    submit = SubmitField(_l('Register')) 

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()

        if user is not None:
            raise ValidationError(_('Username is already taken!!'))
    

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()

        if user is not None:
            raise ValidationError(_('Email is already taken!!'))

    def validate_password(self, password):
        password = password.data
        errors = []
        if len(password) < 8:
            errors.append(f"Password must be at least 8 characters long.")
        if not re.search(r'[A-Za-z]', password):
            errors.append('Must contain at least one letter.')
        if not re.search(r'[0-9]', password):
            errors.append('Must contain at least one number.')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append('Must contain at least one special character.')
        
        if errors:
            raise ValidationError('<br>'.join(errors))

class ResetPasswordRequestForm(FlaskForm):
    email = StringField(_l('Email'), validators=[DataRequired(), Email()])
    submit = SubmitField(_l('Proceed'))


class ResetPasswordForm(FlaskForm):
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    confirm_password = PasswordField(
        _l('Confirm Password'), validators=[EqualTo('password'), DataRequired()]) 
    submit = SubmitField(_l('Reset Password')) 