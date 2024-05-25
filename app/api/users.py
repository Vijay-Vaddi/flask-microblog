from app.api import bp
from app.models import User
from app import db
from flask import jsonify, request, current_app, url_for, abort
from app.api.errors import bad_request
from app.api.auth import token_auth

# returns a single user
@bp.route('/users/<int:id>', methods=['GET'])
@token_auth.login_required
def get_user(id):
    return jsonify(User.query.get_or_404(id).to_dict())

# returns all users
@bp.route('/users', methods=['GET'])
@token_auth.login_required
def get_users():
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    return User.to_collection_dict(User.query, page, per_page, 'api.get_users')

# returns a single users followers
@bp.route('/users/<int:id>/followers', methods=['GET'])
@token_auth.login_required
def get_followers(id):
    user = User.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)

    return User.to_collection_dict(user.followers, page, per_page, 
                                   'api.get_followers', id=id)

# returns this user's following users
@bp.route('/users/<int:id>/following', methods=['GET'])
@token_auth.login_required
def get_following(id):
    user = User.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)

    return User.to_collection_dict(user.followed, page, per_page,
                                   'api.get_following', id=id)

# add/register new users
@bp.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    if 'username' not in data or 'email' not in data or 'password' not in data:
        return bad_request('must include username, email and password')
    if User.query.filter_by(username=data['username']).first():
        return bad_request('Username taken!! Please try again.')
    if User.query.filter_by(email=data['email']).first():
        return bad_request('Email taken!! Please try again.')
    user = User()
    user.from_dict(data, new_user=True)
    db.session.add(user)
    db.session.commit()

    return user.to_dict(), 201, {'Location': url_for('api.get_user', id=user.id)}

# update user info 
@bp.route('/users/<int:id>', methods=['PUT'])
@token_auth.login_required
def update_user(id):
    if token_auth.current_user().id !=id:
        abort(403)
    user = User.query.get_or_404(id)
    data = request.get_json()

    if 'username' in data and data['username']!=user.username \
          and User.query.filter_by(username=data['username']).first():
        return bad_request('Username taken!! Please try again.')
    
    if 'email' in data and data['email']!=user.email \
          and User.query.filter_by(email=data['email']):
        return bad_request('Email taken!! Please try again.')
    
    user.from_dict(data, new_user=False)
    db.session.commit()
    return user.to_dict()
