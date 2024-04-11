from flask_wtf import FlaskForm
from flask_wtf.form import _Auto
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length
from app.models import User

class LoginForm(FlaskForm):

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me?')
    submit = SubmitField('Log in')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField(
        'Confirm Password', validators=[EqualTo('password'), DataRequired()]) 
    submit = SubmitField('Register') 

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()

        if user is not None:
            raise ValidationError('Username is already taken!!')
    

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()

        if user is not None:
            raise ValidationError('Email is already taken!!')
        

class UpdateUserProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Save Changes')

    def __init__(self, original_username, *args, **kwargs):
        super(UpdateUserProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username
    
    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=username)

            if user is not None:
                raise ValidationError("Username taken. Please use a different username")
            