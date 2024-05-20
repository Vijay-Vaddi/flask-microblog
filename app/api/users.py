from app.api import bp

# returns a single user
@bp.route('/users/<int:id>', methods=['GET'])
def get_user(id):
    pass

# returns all users
@bp.route('/users', methods=['GET'])
def get_users():
    pass

# returns a single users followers
@bp.route('/users/<int:id>/followers', methods=['GET'])
def get_followers(id):
    pass

# returns this user's following users
@bp.route('/users/<int:id>/following', methods=['GET'])
def get_following(id):
    pass

# add/register new users
@bp.route('/users', methods=['POST'])
def create_user(id):
    pass

# update user info 
@bp.route('/users/<int:id>', methods=['PUT'])
def update_user(id):
    pass


