from app import app, db
from flask import render_template, redirect, flash, url_for, request
from flask_login import login_user, current_user, logout_user, login_required
from app.forms import LoginForm, RegistrationForm, UpdateUserProfileForm 
from app.forms import Postform, ResetPasswordForm
from app.models import User, Post
from urllib.parse import urlsplit
from datetime import datetime, timezone
from app.email import send_password_reset_mail


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    
    form = Postform()

    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Post submitted')
        return redirect(url_for('index'))
    
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(
        page=page, per_page=app.config['POSTS_PER_PAGE'], error_out=False)
    
    next_url = url_for('index', page=posts.next_num) \
                        if posts.has_next else None
    prev_url = url_for('index', page=posts.prev_num) \
                        if posts.has_prev else None
    
    return render_template("index.html", title='Home', 
                           posts=posts.items, form=form, 
                           next_url=next_url, prev_url=prev_url, page=page)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))  
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if user is None or not user.check_password(password=form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))

        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc!='':
            return redirect(url_for("index"))
        return redirect(next_page)
    return render_template('/login.html', title='Log In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['POST', 'GET'])
def register():
    # redirect if logged in
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegistrationForm()

    # 
    if form.validate_on_submit():
        user = User(username=form.username.data,
                    email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration Success!')
        return redirect(url_for('login'))
    
    return render_template('register.html', title = 'Register User', form=form)


@app.route('/user-profile/<username>')
@login_required
def user_profile(username): #=current_user.username

    print(current_user)
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = user.post.order_by(Post.timestamp.desc()).paginate(
        page=page, per_page=app.config['POSTS_PER_PAGE'], error_out=False)
    
    next_url = url_for('user_profile', username=username, page=posts.next_num) \
                                    if posts.has_next else None
    prev_url = url_for('user_profile', username=username, page=posts.prev_num) \
                                    if posts.has_prev else None
    
    return render_template('user_profile.html', user=user, posts=posts,
                           next_url=next_url, prev_url=prev_url)


@app.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():

    form = UpdateUserProfileForm(current_user.username)

    if form.validate_on_submit():

        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()

        flash('Changes saved.')
        return redirect(url_for('edit_profile'))
    # to pre populate user info in the form to edit
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me

    return render_template('edit_profile.html', title='Edit Profile', form=form)


@app.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('You can not follow yourself')
        return redirect(url_for('index'))
    current_user.follow(user)
    db.session.commit()
    flash('You are now following {}'.format(username))
    return redirect(url_for('user_profile', username=username))


@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('You can not unfollow yourself')
        return redirect(url_for('index'))
    if not current_user.is_following(user):
        flash(f"You are not following {username} yet!")

    current_user.unfollow(user)
    db.session.commit()
    flash('You are now following {}'.format(username))
    return redirect(url_for('user_profile', username=username))


@app.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page=page, per_page=app.config['POSTS_PER_PAGE'], error_out=False)

    next_url = url_for('index', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('index', page=posts.prev_num) if posts.has_prev else None
    return render_template('index.html', title='Explore', posts=posts.items,
                           next_url=next_url, prev_url=prev_url) 


@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        redirect(url_for('index'))
    
    form = ResetPasswordForm()

    if form.validate_on_submit:
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_mail(user)
        flash('Please check your email for further instructions')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html', form=form, title='Reset Password')


