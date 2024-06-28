from app.main import bp
from flask import redirect, render_template, flash, url_for, \
                            request, current_app, g, session, jsonify
from app.main.forms import EmptyForm, Postform, UpdateUserProfileForm, \
                            SearchForm, MessageForm, CommentForm
from flask_login import current_user, login_required
from app.models import db, User, Post, Message, Notification, Comment, \
                            PostLike, CommentLike
from datetime import datetime, timezone
from flask_babel import get_locale, _
from langdetect import detect
from app.main.picture_handler import add_pic
from app.translate import translate


@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()
        g.search_form = SearchForm()
    g.locale = str(get_locale())

#######################################################
########## PRIVATE AND PUBLIC FEED SECTION  ###########
#######################################################

@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    comment_form = CommentForm()
    form = Postform()
    if form.validate_on_submit():
        try:
            language = detect(form.post.data)
        except:
            language=''
    
        post = Post(body=form.post.data, author=current_user, 
                    language=language)
        # save first to generate post.id 
        db.session.add(post)
        db.session.commit()

        # check if img exist and save  
        if form.post_image.data:
            post_image = add_pic(form.post_image.data, post=post)
            post.post_image=post_image
            db.session.add(post)
            db.session.commit()

        flash(_('Post submitted'))
        return redirect(url_for('main.index'))
    
    # filter out posts by current user for index page  
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().filter(Post.user_id!=current_user.id).paginate(
        page=page, per_page=current_app.config['POSTS_PER_PAGE'], 
                    error_out=False)
    
    # used for limiting pages to display
    total_pages=posts.pages

    next_url = url_for('main.index', page=posts.next_num) \
                        if posts.has_next else None
    prev_url = url_for('main.index', page=posts.prev_num) \
                        if posts.has_prev else None
    
    return render_template("index.html", title='Home', page=page, max=max, min=min,
                           posts=posts.items, form=form, total_pages=total_pages, 
                           next_url=next_url, prev_url=prev_url, comment_form=comment_form)


@bp.route('/explore/')
@login_required
def explore():
    comment_form = CommentForm()
    
    page = request.args.get('page', 1, type=int)    
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page=page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
    total_pages=posts.pages

    next_url = url_for('main.explore', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('main.explore', page=posts.prev_num) if posts.has_prev else None
    
    return render_template('index.html', title='Explore', posts=posts.items, 
                           max=max, min=min, next_url=next_url, prev_url=prev_url, 
                           total_pages=total_pages, page=page, comment_form=comment_form) 


#######################################################
##############   USER PROFILE SECTION  ################
#######################################################

@bp.route('/user-profile/<username>')
@login_required
def user_profile(username): 
    form = MessageForm()
    comment_form= CommentForm()
    
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = user.post.order_by(Post.timestamp.desc()).paginate(
        page=page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
    total_pages=posts.pages    
    
    next_url = url_for('main.user_profile', username=username, page=posts.next_num) \
                                    if posts.has_next else None
    prev_url = url_for('main.user_profile', username=username, page=posts.prev_num) \
                                    if posts.has_prev else None
    
    return render_template('user_profile.html', user=user, posts=posts.items, title='User Profile',
                           next_url=next_url, prev_url=prev_url, page=page, comment_form=comment_form,
                           total_pages=total_pages, min=min, max=max, form=form)


@bp.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = UpdateUserProfileForm(current_user.username)

    if form.validate_on_submit():
        if form.profile_pic.data:
            pic = add_pic(form.profile_pic.data)
            current_user.profile_pic = pic 

        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()

        flash(_('Changes saved.'))
        return redirect(url_for('main.edit_profile'))
    
    # to pre populate user info in the form to edit
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me

    return render_template('edit_profile.html', title='Edit Profile', form=form )


@bp.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    
    # check if user exists and is not current user 
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
    
    # check if user exists and is not current user 
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


@bp.route('/user-profile/<username>/popup')
@login_required
def user_popup(username):
    user = User.query.filter_by(username=username).first_or_404()
    
    form = EmptyForm()
    
    return render_template('user_popup.html', user=user, form=form, title='user profile')


#######################################################
################   POST'S SECTION  ####################
#######################################################

@bp.route('/edit-post/<id>', methods=['POST', 'GET'])
@login_required
def edit_post(id):
    post = Post.query.get(id) 
    
    form = Postform()
    if form.validate_on_submit():
        
        post.body = form.post.data 
        # check for image
        if form.post_image.data:
            post_image = add_pic(form.post_image.data, post=post)
            post.post_image=post_image
        
        db.session.add(post)
        db.session.commit()
        flash(_('Post edited submitted'))
        return redirect(url_for('main.index'))
    # populate post with existing values
    form.post.data = post
    form.post.label.text= 'Edit your post'
    if post.post_image:
        form.post_image.data=post.post_image
    return render_template('edit_post.html', form=form, title='Edit post')


@bp.route('/delete-post/<id>', methods=['POST', 'GET'])
@login_required
def delete_post(id):
    
    # check if item is post or message and del accordingly
    item = request.args.get('item')
    if item == 'post':
        del_item = Post.query.get(id) 
    elif item == 'message':
        del_item = Message.query.get(id)
    
    db.session.delete(del_item)
    db.session.commit()
    next_url=request.args.get('next')
    return redirect(next_url)

#######################################################
################   MESSSAGE'S SECTION  ################
#######################################################

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
        
        # check for request origin and redirect user back
        if request.args.get('current_page') == 'inbox':
            return redirect(url_for('main.messages'))
        elif request.args.get('current_page') == 'user_profile':
            return redirect(url_for('main.user_profile', username=receiver))
    
    return render_template('send_message.html', title='Send message',
                           form=form, receiver=receiver)

# view messages
@bp.route('/messages')
@login_required
def messages():
    # send messagefrom obj to reply and message back
    form = MessageForm()

    sent = request.args.get('sent', False, type=bool)

    current_user.last_message_read_time = datetime.now(timezone.utc)
    current_user.add_notification('unread_message_count', 0)
    db.session.commit()
    page = request.args.get('page', 1, type=int)

    # check if request is for inbox items or sent items 
    if sent: 
        messages = current_user.messages_sent.order_by(
                                        Message.timestamp.desc()).paginate(page=page, 
                                        per_page=current_app.config['POSTS_PER_PAGE'], 
                                        error_out=False)
        title = 'sent'
    else:
        messages = current_user.messages_received.order_by(
                                        Message.timestamp.desc()).paginate(page=page, 
                                        per_page=current_app.config['POSTS_PER_PAGE'], 
                                        error_out=False)
        title = 'inbox'

    total_pages=messages.pages
    next_url = url_for('main.messages', page=messages.next_num) if messages.has_next else None
    prev_url = url_for('main.messages', page=messages.prev_num) if messages.has_prev else None
  
    return render_template('messages.html', messages=messages, page=page, 
                           total_pages=total_pages, min=min, max=max, form=form,
                           next_url=next_url, prev_url=prev_url, title=title)


#######################################################
#########    ADDITIONAL FEATURES SECTION    ###########
#######################################################

#full text search of posts 
@bp.route('/search', methods=['GET'])
@login_required
def search():
    if not g.search_form.validate():
        return redirect(url_for('main.explore'))
        
    page = request.args.get('page', 1, type=int)
    posts, total = Post.search(g.search_form.query.data, page, current_app.config['POSTS_PER_PAGE'])
    
    next_url = url_for('main.search', query=g.search_form.query.data, page=page+1)\
        if total > page*current_app.config['POSTS_PER_PAGE'] else None
    prev_url = url_for('main.search', query=g.search_form.query.data, page=page-1)\
        if page > 1 else None
    
    total_pages=total//current_app.config['POSTS_PER_PAGE']
    return render_template('search.html', title=_('search'), posts=posts,
                           next_url=next_url, prev_url=prev_url, total_pages=total_pages,
                           min=min, max=max, page=page)


@bp.route('/notifications')
@login_required
def notifications():
    # since : last notifications time
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


@bp.route('/translate', methods=['GET', 'POST'])
@login_required
def translate_text():
    data = request.get_json()
    return {'text': translate(
        data['text'], data['source_language'],
        data['dest_language']
    )}

#######################################################
##############     COMMENTS SECTION    ################
#######################################################

# for posting comments
@bp.route('/comment/<post_id>', methods=['GET', 'POST'])
@login_required
def comment(post_id):
    form = CommentForm()
    
    post = Post.query.filter_by(id=post_id).first_or_404()
    body = form.body.data
    if form.validate_on_submit():
        comment = Comment(body=body, author=current_user,
                          post=post)
        
        db.session.add(comment)
        db.session.commit() 
    
    return jsonify({
            'html':render_template('comment.html', comment_form=form, comment=comment),
            'text':comment.body}) 
    
    # else add exception 

# edit comments
@bp.route('/edit-comment/<id>', methods=['GET', 'POST'])
@login_required
def edit_comment(id):
    comment = Comment.query.get_or_404(id)
    
    form = CommentForm()
    if form.validate_on_submit():
        comment.body = form.body.data
        db.session.add(comment)
        db.session.commit()
    
    return {'message':'Edit successful',
                    'text':comment.body}

# delete comments
@bp.route('/delete-comment/<id>', methods=['GET', 'POST'])
@login_required
def delete_comment(id):
    comment = Comment.query.get_or_404(id)
    
    if comment:
        db.session.delete(comment)
        db.session.commit()
        return jsonify({'message':'Comment Deleted',
                'comment_id':id}), 200
    else:
        return 'Comment does not exists', 404


######################################################
################   LIKES FEATURE   ###################
######################################################

@bp.route('/post-like/<int:post_id>', methods=['GET', 'POST'])
@login_required
def post_like(post_id):
    post = Post.query.get_or_404(post_id)
    
    # check if user liked a post
    post_like = PostLike.query.filter_by(user_id=current_user.id, post_id=post_id).first()
    
    # if liked, unlike
    if post_like:
        db.session.delete(post_like)
        db.session.commit()
        return jsonify({'Message': 'unliked',
                        'post_id':post_id,
                        'user_id':current_user.id,
                        'like_count':post.likes.count()}), 200
    # else like post
    else: 
        post_like = PostLike(user_id=current_user.id, post_id=post_id)
        db.session.add(post_like)
        db.session.commit()
        return jsonify({'Message': 'liked',
                        'post_id':post_id,
                        'user_id':current_user.id,
                        'like_count':post.likes.count()}), 200
    

@bp.route('/comment-like/<int:comment_id>', methods=['GET', 'POST'])
@login_required
def comment_like(comment_id):

    comment = Comment.query.get_or_404(comment_id)
    # check if user liked a post
    comment_like = CommentLike.query.filter_by(user_id=current_user.id, comment_id=comment_id).first()

    # if liked, unlike
    if comment_like:
        db.session.delete(comment_like)
        db.session.commit()
        return jsonify({'Message': 'unliked',
                        'comment_id':comment_id,
                        'user_id':current_user.id,
                        'like_count':comment.likes.count()}), 200
    # else like comment
    else: 
        comment_like = CommentLike(user_id=current_user.id, comment_id=comment_id)
        db.session.add(comment_like)
        db.session.commit()
        return jsonify({'Message': 'liked',
                        'comment_id':comment_id,
                        'user_id':current_user.id,
                        'like_count':comment.likes.count()}), 200