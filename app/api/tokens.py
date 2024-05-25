'''auth system for non browser clients to log in and 
request resources'''
from app import db
from app.api import bp
from app.api.auth import basic_auth, token_auth

# returns token if the user is valid
@bp.route('/tokens', methods=['POST'])
@basic_auth.login_required
def get_token():
    token = basic_auth.current_user().get_token()
    db.session.commit()
    return {'token':token}

@bp.route('/tokens', methods=['DELETE'])
@token_auth.login_required
def revoke_token():
    token_auth.current_user().revoke_token()
    db.session.commit()
    return '', 204

