from app.main import bp
from flask import redirect, render_template, flash, url_for, \
                            request, current_app, g
from app.main.forms import EmptyForm, Postform, UpdateUserProfileForm, \
                            SearchForm, MessageForm
from flask_login import current_user, login_required
from app.models import db, User, Post, Message, Notification
from datetime import datetime, timezone
from flask_babel import get_locale, _
from langdetect import detect



@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()
        g.search_form = SearchForm()
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
    
    return render_template("index.html", title='Home', 
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
    
    return render_template('user_profile.html', user=user, posts=posts,
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

    return render_template('edit_profile.html', title='Edit Profile', form=form)


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


@bp.route('/explore/')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page=page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)

    print(posts.items)

    next_url = url_for('main.explore', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('main.explore', page=posts.prev_num) if posts.has_prev else None
    return render_template('index.html', title='Explore', posts=posts.items,
                           next_url=next_url, prev_url=prev_url) 


@bp.route('/search', methods=['GET'])
@login_required
def search():
    print('inside search')

    if not g.search_form.validate():
        print('validate')
        return redirect(url_for('main.explore'))
        

    page = request.args.get('page', 1, type=int)
    posts, total = Post.search(g.search_form.query.data, page, current_app.config['POSTS_PER_PAGE'])
    next_url = url_for('main.search', query=g.search_form.query.data, page=page+1)\
        if total > page*current_app.config['POSTS_PER_PAGE'] else None
    prev_url = url_for('main.search', query=g.search_form.query.data, page=page-1)\
        if page > 1 else None
    print('after')
    return render_template('search.html', title=_('search'), posts=posts,
                           next_url=next_url, prev_url=prev_url)


@bp.route('/edit-post/<id>', methods=['POST', 'GET'])
@login_required
def edit_post(id):
    
    post = Post.query.get(id) 
    form = Postform()
    if form.validate_on_submit():
        # test driven development,
        post.body = form.post.data 
        db.session.commit()
        flash(_('Post edited submitted'))
        return redirect(url_for('main.index'))
    form.post.data = post
    return render_template('edit_post.html', form=form)


@bp.route('/delete-post/<id>', methods=['POST', 'GET'])
@login_required
def delete_post(id):
    
    post = Post.query.get(id) 
    form = Postform()
    if form.validate_on_submit():
        # test driven development,
        post.body = form.post.data 
        db.session.commit()
        flash(_('Post edited submitted'))
        return redirect(url_for('main.index'))
    form.post.data = post
    return render_template('edit_post.html', form=form)


@bp.route('/user-profile/<username>/popup')
@login_required
def user_popup(username):
    user = User.query.filter_by(username=username).first_or_404()
    form = EmptyForm()
    return render_template('user_popup.html', user=user, form=form)


@bp.route('/send-message/<receiver>', methods=['GET', 'POST'])
@login_required
def send_message(receiver):
    user = User.query.filter_by(username=receiver).first_or_404()
    form = MessageForm()

    if form.validate_on_submit():
        msg = Message(author = current_user, receiver=user,
                      body=form.message.data)
        db.session.add(msg)
        user.add_notification('unread_message_count', user.new_messages())
        db.session.commit()
        flash('Message sent successfully!')
        return redirect(url_for('main.user_profile', username=receiver))
    
    return render_template('send_message.html', title='Send message',
                           form=form, receiver=receiver)


@bp.route('/messages')
@login_required
def messages():
    current_user.last_message_read_time = datetime.now(timezone.utc)
    current_user.add_notification('unread_message_count', 0)
    db.session.commit()

    page = request.args.get('page', 1, type=1)
    messages = current_user.messages_received.order_by(
        Message.timestamp.desc()).paginate(page=page, 
                                    per_page=current_app.config['POSTS_PER_PAGE'], 
                                    error_out=False)
    next_url = url_for('main.messages', page=messages.next_num) if messages.has_next else None
    prev_url = url_for('main.messages', page=messages.prev_num) if messages.has_prev else None
  
    return render_template('messages.html', messages=messages, 
                           next_url=next_url, prev_url=prev_url)


@bp.route('/notifications')
@login_required
def notifications():
    since = request.args.get('since', 0.0, type=float)
    notifications = current_user.notifications.filter(
        Notification.timestamp > since).order_by(Notification.timestamp.asc()) 

    return [{
        'name': n.name,
        'data': n.get_data(),
        'timestamp':n.timestamp
    } for n in notifications ] 


@bp.route('/export_posts')
@login_required
def export_posts():

    if current_user.get_task_in_progress('export_posts'):
        flash('Export already in progress')
    else:
        current_user.launch_task("export_posts", "Exporting posts")
        db.session.commit()
    
    return redirect(url_for('main.user_profile', username=current_user.username))
