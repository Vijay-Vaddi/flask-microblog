from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
from app import db
from app.models import User
from app.api.errors import error_response

basic_auth = HTTPBasicAuth()

# function to check credentials and return user
@basic_auth.verify_password
def verify_password(username, password):
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        return user

# function to handle 401 unauthorized error
@basic_auth.error_handler
def basic_auth_error(status):
    return error_response(status)

