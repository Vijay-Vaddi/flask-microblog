from app import db, login
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5

followers = db.Table(
    'followers',
    db.Column('follower_id',db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id',db.Integer, db.ForeignKey('user.id'))
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(64), index=True, unique = True)
    email = db.Column(db.String(128), index=True, unique = True)
    password_hash = db.Column(db.String(128))
    post = db.relationship('Post', backref='author', lazy='dynamic')
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default = datetime.now(timezone.utc))

    followed = db.relationship(
        'User',  secondary = followers,
        primaryjoin = (followers.c.follower_id == id),
        secondaryjoin = (followers.c.followed_id == id),
        backref = db.backref('followers', lazy='dynamic'), lazy='dynamic')

    def __repr__(self) -> str:
        return f"{self.username} , {self.email}"
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f"https://www.gravatar.com/avatar/4f9fecabbd77fba02d2497f880f44e6f?s={size}&d=identicon"

    def follow(self, user): #pass a user to follow
        if not self.is_following(user):
            self.followed.append(user)
    
    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    #check is passed user is among list of followed ids 
    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    def followed_posts(self):
        followed_posts = Post.query.join(
            #first get all the posts where followed_id 
            #== post's authors id, i e only followed posts. 
            followers, (Post.user_id == followers.c.followed_id)).filter(
                #then get those posts where follower_id == current_user.id
                followers.c.follower_id == self.id)
        #to include self posts in the timeline. 
        return followed_posts.union(self.post).order_by(Post.timestamp.desc())


@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))

class Post(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default = datetime.now(timezone.utc))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self) -> str:
        return f"{self.body}"
    

