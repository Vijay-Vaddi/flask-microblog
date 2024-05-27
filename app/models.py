import redis.exceptions
import rq.exceptions
from app import db, login
from datetime import datetime, timezone, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5
import jwt, secrets
from time import time
from flask import current_app
from app.search import add_to_index, query_index, remove_from_index
import json, rq, redis
from flask import url_for


# for collections of resources
class PaginatedAPIMixin(object):
    @staticmethod
    def to_collection_dict(query, page, per_page, endpoint, **kwargs):
        resources = db.paginate(query, per_page=per_page, 
                                page=page, error_out=False)
        
        data = {
            'items':[item.to_dict() for item in resources.items],
            '_meta':{
                'page':page,
                'per_page':per_page,
                'total_pages':resources.pages,
                'total_items':resources.total,
            },
            '_links':{
                'self':url_for(endpoint, page=page, per_page=per_page,
                               **kwargs),
                'next':url_for(endpoint, page=page+1, per_page=per_page,
                               **kwargs) if resources.has_next else None,
                'prev':url_for(endpoint, page=page -1, per_page=per_page,
                               **kwargs) if resources.has_prev else None,                               
            }

        }
        return data

# many-many table for follower-following relationship between users 
followers = db.Table(
    'followers',
    db.Column('follower_id',db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id',db.Integer, db.ForeignKey('user.id'))
)

class User(PaginatedAPIMixin, UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(64), index=True, unique = True)
    email = db.Column(db.String(128), index=True, unique = True)
    password_hash = db.Column(db.String(128))
    post = db.relationship('Post', backref='author', lazy='dynamic')
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default = datetime.now(timezone.utc))
    profile_pic = db.Column(db.String(64), nullable = True, default='default_prof_pic.png')

    # relationships for follow table -exists only in model space
    followed = db.relationship(
        'User',  secondary = followers,
        primaryjoin = (followers.c.follower_id == id),
        secondaryjoin = (followers.c.followed_id == id),
        backref = db.backref('followers', lazy='dynamic'), lazy='dynamic')
    
    # relationships for message table
    messages_sent = db.relationship('Message', foreign_keys='Message.sender_id', 
                                   backref='author', lazy='dynamic')
    messages_received = db.relationship('Message', foreign_keys='Message.receiver_id',
                                        backref='receiver', lazy='dynamic')
    
    last_message_read_time = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    # relationship for notifications table
    notifications = db.relationship('Notification', backref='user',
                              lazy='dynamic')
    
    tasks = db.relationship('Task', backref='user', lazy='dynamic')

    token = db.Column(db.String(32), index=True, unique=True)
    token_expiration = db.Column(db.DateTime)

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
    
    def new_messages(self):
        last_read_time = self.last_message_read_time or datetime(1900,1,1)

        return Message.query.filter_by(receiver=self).filter(
            Message.timestamp > last_read_time).count()
    
    def add_notification(self, name, data):
        self.notifications.filter_by(name=name).delete()
        n = Notification(name=name, payload_json=json.dumps(data), user=self)
        db.session.add(n)
        return n 
    
    # helper methods for redis queues
    # create and launch a task queue
    def launch_task(self, name, description, *args, **kwargs):
        rq_job = current_app.task_queue.enqueue('app.tasks.'+name, self.id,
                                                *args, **kwargs)
        task = Task(id=rq_job.get_id(), name=name, description=description,
                    user=self)
        db.session.add(task)
        return task
    
    # return all running tasks
    def get_tasks_in_progress(self):
        return Task.query.filter_by(user=self, complete=False).all()
    
    # return particular task, used to generate progress
    def get_task_in_progress(self, name):
        return Task.query.filter_by(name=name, user=self, complete=False).first() 
    
    # Helper methods for API
    # to_dict: returns user's data in dict format 
  
    def to_dict(self, include_email=False):
        data = {
            'id': self.id,
            'username':self.username,
            'last_seen':self.last_seen.isoformat()+'Z',
            'about_me':self.about_me,
            'follower':self.followers.count(),
            'followed':self.followed.count(),
            '_links':{
                'self':url_for('api.get_user', id=self.id),
                'followers':url_for('api.get_followers', id=self.id),
                'followers':url_for('api.get_following', id=self.id),
                'avatar':self.avatar(128),
            }
        }

        if include_email:
            data['email']=self.email
        return data
    
    def from_dict(self, data, new_user=False):
        for field in ['username', 'email', 'about_me']:
            if field in data:
                setattr(self, field, data[field])
        if new_user and 'password' in data:
            self.set_password(data['password'])

    # for API token auth
    def get_token(self, expires_in=3600):
        now = datetime.now(timezone.utc)
        if self.token and self.token_expiration.replace(
                tzinfo=timezone.utc) > now + timedelta(seconds=60):
            return self.token
        self.token = secrets.token_hex(16)
        self.token_expiration = now + timedelta(seconds=expires_in)
        db.session.add(self)
        return self.token
    
    def revoke_token(self):
        self.token_expiration = datetime.now(timezone.utc) - timedelta(seconds=1)

    @staticmethod
    def check_token(token):
        user = User.query.filter_by(token=token).first()
        if user is None or user.token_expiration.replace(
                tzinfo=timezone.utc) < datetime.now(timezone.utc):
            return None
        return user

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

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.now(timezone.utc))

    def __repr__(self) -> str:
        return f"Message {self.body}"

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    # to support other notifications besides messages. 
    name = db.Column(db.String(128), index=True)
    timestamp = db.Column(db.Float,  default=time, index=True) #unix time stamp to make it friendly on js side
    payload_json = db.Column(db.Text)

    def get_data(self):
        return json.loads(str(self.payload_json))

class Task(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(128), index=True)
    description = db.Column(db.String(128))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    complete = db.Column(db.Boolean, default = False)

    def get_rq_job(self):
        try:
            rq_job = rq.job.Job.fetch(self.id, connection=current_app.redis)
        except (redis.exceptions.RedisError, rq.exceptions.NoSuchJobError):
            return None
        return rq_job

    def get_progress(self):
        job = self.get_rq_job()
        return job.meta.get('progress', 0) if job is not None else 100



#to hook before_commit, after_commit event handlers to SQLalchemy event listeners
db.event.listen(db.session, 'before_commit', Post.before_commit)
db.event.listen(db.session, 'after_commit', Post.after_commit) 
