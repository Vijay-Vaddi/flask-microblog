from flask_wtf import FlaskForm
from flask_wtf.form import _Auto
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, Length
from app.models import User
from flask_babel import _, lazy_gettext as _l
from flask import request

class UpdateUserProfileForm(FlaskForm):
    username = StringField(_l('Username'), validators=[DataRequired()])
    about_me = TextAreaField(_l('About me'), validators=[Length(min=0, max=140)])
    submit = SubmitField(_l('Save Changes'))

    def __init__(self, original_username, *args, **kwargs):
        super(UpdateUserProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username
    
    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=username)

            if user is not None:
                raise ValidationError(_("Username taken. Please use a different username"))

class Postform(FlaskForm):
    post = TextAreaField(_l('Write your post here'), 
                         validators=[DataRequired(), Length(min=1, max=140)])
    submit = SubmitField(_l('Post'))

class SearchForm(FlaskForm):
    query = StringField(_l('Search'), validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        
        if 'meta' not in kwargs:
            kwargs['meta'] = {'csrf':False} 
        
        super(SearchForm, self).__init__(*args, **kwargs)
        