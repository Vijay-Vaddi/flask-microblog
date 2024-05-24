# helper functions to handle errors
from werkzeug.http import HTTP_STATUS_CODES
from werkzeug.exceptions import HTTPException
from app.api import bp

# Generate structured error response for HTTP status codes
def error_response(status_code, message=None):
    payload = {'error':HTTP_STATUS_CODES.get(status_code, 'Unknown error')}

    if message:
        payload['message']=message
    return payload, status_code

# to handle only 400(bad request) errors as it is most common 
def bad_request(message):
    return error_response(400, message)

# to return all errors in json format
@bp.errorhandler(HTTPException)
def handle_exception(e):
    return error_response(e.code, str(e))

