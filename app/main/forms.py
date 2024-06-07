from flask_wtf import FlaskForm
from flask_wtf.form import _Auto
from flask_wtf.file import FileAllowed, FileField
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, Length
from app.models import User
from flask_babel import _, lazy_gettext as _l
from flask import request
import re

class UpdateUserProfileForm(FlaskForm):
    username = StringField(_l('Username'), validators=[DataRequired()])
    about_me = TextAreaField(_l('About me'), validators=[Length(min=0, max=140)])
    profile_pic = FileField('Profile picture', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif'])])
    submit = SubmitField(_l('Save Changes'))

    def __init__(self, original_username, *args, **kwargs):
        super(UpdateUserProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username
    
    def validate_username(self, username):
        username_allowed_chars = re.compile(r'^[a-zA-Z0-9_@]+$')
        username=username.data
        errors =[]
        
        if username != self.original_username:
            user = User.query.filter_by(username=username).first()
            if user is not None:
                raise ValidationError(_("Username taken. Please use a different username"))
        
        if len(username) > 16 or len(username) <5:
            errors.append(f"Length must be  5-16 characters!!")

        if ' ' in username:
            errors.append(f"Can not contain empty spaces!")
        
        if not username_allowed_chars.match(username):
            errors.append(f"Only alphanumericals and _ @ are allowed!")

        if errors:
            raise ValidationError('<br>'.join(errors))

class Postform(FlaskForm):
    post = TextAreaField(_l('Write your post here'), 
                         validators=[DataRequired(), Length(min=1, max=280)])
    post_image = FileField('', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif','webp'])])
    submit = SubmitField(_l('Post'))

class SearchForm(FlaskForm):
    query = StringField(_l('Search'), validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        
        if 'meta' not in kwargs:
            kwargs['meta'] = {'csrf':False} 
        
        super(SearchForm, self).__init__(*args, **kwargs)

class EmptyForm(FlaskForm):
    submit = SubmitField('Submit')

class MessageForm(FlaskForm):
    message = TextAreaField('Message', validators=[DataRequired(), 
                                                    Length(min=1, max=140)])
    submit = SubmitField('Submit')