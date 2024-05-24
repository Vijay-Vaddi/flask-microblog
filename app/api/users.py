from app.api import bp
from app.models import User
from app import db
from flask import jsonify, request, current_app

# returns a single user
@bp.route('/users/<int:id>', methods=['GET'])
def get_user(id):
    return jsonify(User.query.get_or_404(id).to_dict())

# returns all users
@bp.route('/users', methods=['GET'])
def get_users():
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    return User.to_collection_dict(User.query, page, per_page, 'api.get_users')

# returns a single users followers
@bp.route('/users/<int:id>/followers', methods=['GET'])
def get_followers(id):
    user = User.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)

    return User.to_collection_dict(user.followers, page, per_page, 
                                   'api.get_followers', id=id)

# returns this user's following users
@bp.route('/users/<int:id>/following', methods=['GET'])
def get_following(id):
    user = User.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)

    return User.to_collection_dict(user.followed, page, per_page,
                                   'api.get_following', id=id)

# add/register new users
@bp.route('/users', methods=['POST'])
def create_user():
    pass

# update user info 
@bp.route('/users/<int:id>', methods=['PUT'])
def update_user(id):
    pass


