# from flask_wtf import FlaskForm
# from flask_wtf.form import _Auto
# from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
# from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length
# from app.models import User
# from flask_babel import _, lazy_gettext as _l


# class LoginForm(FlaskForm):

#     username = StringField(_l('Username'), validators=[DataRequired()])
#     password = PasswordField(_l('Password'), validators=[DataRequired()])
#     remember_me = BooleanField(_l('Remember Me?'))
#     submit = SubmitField(_l('Log in'))


# class RegistrationForm(FlaskForm):
#     username = StringField(_l('Username'), validators=[DataRequired()])
#     email = StringField(_l('Email'), validators=[DataRequired(), Email()])
#     password = PasswordField(_l('Password'), validators=[DataRequired()])
#     confirm_password = PasswordField(
#         _l('Confirm Password'), validators=[EqualTo('password'), DataRequired()]) 
#     submit = SubmitField(_l('Register')) 

#     def validate_username(self, username):
#         user = User.query.filter_by(username=username.data).first()

#         if user is not None:
#             raise ValidationError(_('Username is already taken!!'))
    

#     def validate_email(self, email):
#         user = User.query.filter_by(email=email.data).first()

#         if user is not None:
#             raise ValidationError(_('Email is already taken!!'))
        

# class UpdateUserProfileForm(FlaskForm):
#     username = StringField(_l('Username'), validators=[DataRequired()])
#     about_me = TextAreaField(_l('About me'), validators=[Length(min=0, max=140)])
#     submit = SubmitField(_l('Save Changes'))

#     def __init__(self, original_username, *args, **kwargs):
#         super(UpdateUserProfileForm, self).__init__(*args, **kwargs)
#         self.original_username = original_username
    
#     def validate_username(self, username):
#         if username.data != self.original_username:
#             user = User.query.filter_by(username=username)

#             if user is not None:
#                 raise ValidationError(_("Username taken. Please use a different username"))

# class Postform(FlaskForm):
#     post = TextAreaField(_l('Write your post here'), 
#                          validators=[DataRequired(), Length(min=1, max=140)])
#     submit = SubmitField(_l('Post'))

# class ResetPasswordRequestForm(FlaskForm):
#     email = StringField(_l('Email'), validators=[DataRequired(), Email()])
#     submit = SubmitField(_l('Proceed'))

# class ResetPasswordForm(FlaskForm):
#     password = PasswordField(_l('Password'), validators=[DataRequired()])
#     confirm_password = PasswordField(
#         _l('Confirm Password'), validators=[EqualTo('password'), DataRequired()]) 
#     submit = SubmitField(_l('Reset Password')) 