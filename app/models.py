from app import db, login
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5
import jwt
from time import time
from flask import current_app, session
from app.search import add_to_index, query_index, remove_from_index

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

    def get_reset_password_token(self, expiration=600):
        print('inside user model')
        return jwt.encode(
            {'reset-password':self.id, 'exp':time()+expiration}, 
            current_app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def verify_reset_password_token(token):
        # no need for self since user is trying to reset password
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])['reset-password']
        except:
            return None
        return User.query.get(id)
    
@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))
    
class SearchableMixin(object):
    @classmethod
    def search(cls, query, page, per_page):
        ids, total = query_index(cls.__tablename__, query, page, per_page)
        if total == 0:
            return [], 0
        when = []

        for i in range(len(ids)):
            when.append((ids[i], i))

        # pass when to order_by search query score 
        return cls.query.filter(cls.id.in_(ids)).order_by(
            db.case(*when, value=cls.id)), total
    
    # store session activity in temp attribute _change to use after commit
    @classmethod
    def before_commit(cls, session):
        session._change={
            'add':[obj for obj in session.new if isinstance(obj, cls)],
            'update':[obj for obj in session.dirty if isinstance(obj, cls)],
            'deleted':[obj for obj in session.deleted if isinstance(obj, cls)],
        }

    # using _change add/update or delete index by calling functions
    @classmethod
    def after_commit(cls, session):
        for obj in session._change['add']:
            add_to_index(cls.__tablename__, obj)
        for obj in session._change['update']:
            add_to_index(cls.__tablename__, obj)
        for obj in session._change['deleted']:
            remove_from_index(cls.__tablename__, obj)
        session._change = None

    #index all the items in model till date
    @classmethod
    def reindex(cls):
        for obj in cls.query:
            add_to_index(cls.__tablename__, obj)

class Post(SearchableMixin, db.Model):
    id = db.Column(db.Integer, primary_key = True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default = datetime.now(timezone.utc))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    language = db.Column(db.String(5))
    __searchable__ = ['body']

    def __repr__(self) -> str:
        return f"{self.body}"

#to hook before_commit, after_commit event handlers to SQLalchemy event listeners
db.event.listen(db.session, 'before_commit', Post.before_commit)
db.event.listen(db.session, 'after_commit', Post.after_commit) 
