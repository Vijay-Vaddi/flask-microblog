from app.main import bp
from flask import redirect, render_template, flash, url_for, request, current_app, g
from app.main.forms import Postform, UpdateUserProfileForm
from flask_login import current_user, login_required
from app.models import db, User, Post
from datetime import datetime, timezone
from flask_babel import get_locale, _
from langdetect import detect

@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()
        g.locale = str(get_locale())


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    
    form = Postform()

    if form.validate_on_submit():
        try:
            language = detect(form.post.data)
        except:
            language=''
        post = Post(body=form.post.data, author=current_user, 
                    language=language)
        db.session.add(post)
        db.session.commit()
        flash(_('Post submitted'))
        return redirect(url_for('main.index'))
    
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(
        page=page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
    
    next_url = url_for('main.index', page=posts.next_num) \
                        if posts.has_next else None
    prev_url = url_for('main.index', page=posts.prev_num) \
                        if posts.has_prev else None
    
    return render_template("main/index.html", title='Home', 
                           posts=posts.items, form=form, 
                           next_url=next_url, prev_url=prev_url, page=page)


@bp.route('/user-profile/<username>')
@login_required
def user_profile(username): #=current_user.username

    print(current_user)
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = user.post.order_by(Post.timestamp.desc()).paginate(
        page=page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
    
    next_url = url_for('main.user_profile', username=username, page=posts.next_num) \
                                    if posts.has_next else None
    prev_url = url_for('main.user_profile', username=username, page=posts.prev_num) \
                                    if posts.has_prev else None
    
    return render_template('main/user_profile.html', user=user, posts=posts,
                           next_url=next_url, prev_url=prev_url)


@bp.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():

    form = UpdateUserProfileForm(current_user.username)

    if form.validate_on_submit():

        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()

        flash(_('Changes saved.'))
        return redirect(url_for('main.edit_profile'))
    # to pre populate user info in the form to edit
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me

    return render_template('main/edit_profile.html', title='Edit Profile', form=form)


@bp.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(_('User %(username)s not found',username=username))
        return redirect(url_for('index'))
    if user == current_user:
        flash(_('You can not follow yourself'))
        return redirect(url_for('main.index'))
    current_user.follow(user)
    db.session.commit()
    flash(_('You are now following %(username)s',username=username))
    return redirect(url_for('main.user_profile', username=username))


@bp.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(_('User %(username)s not found',username=username))
        return redirect(url_for('main.index'))
    if user == current_user:
        flash(_('You can not unfollow yourself'))
        return redirect(url_for('main.index'))
    if not current_user.is_following(user):
        flash(_('You are not following %(username)s yet',username=username))

    current_user.unfollow(user)
    db.session.commit()
    flash(_('You are now unfollowing %(username)s',username=username))
    return redirect(url_for('main.user_profile', username=username))


@bp.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page=page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)

    next_url = url_for('main.index', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('main.index', page=posts.prev_num) if posts.has_prev else None
    return render_template('main/index.html', title='Explore', posts=posts.items,
                           next_url=next_url, prev_url=prev_url) 
