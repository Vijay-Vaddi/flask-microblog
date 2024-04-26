from app.auth import bp
from flask_login import current_user, login_user, logout_user
from flask import redirect, render_template, url_for, flash, request
from app.auth.forms import RegistrationForm, LoginForm, ResetPasswordForm, ResetPasswordRequestForm
from app import db
from app.models import User
from urllib.parse import urlsplit
from app.auth.email import send_password_reset_email
from flask_babel import _

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))  
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if user is None or not user.check_password(password=form.password.data):
            flash(_('Invalid username or password'))
            return redirect(url_for('auth.login'))

        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc!='':
            return redirect(url_for("main.index"))
        return redirect(next_page)
    return render_template('/auth/login.html', title='Log In', form=form)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@bp.route('/register', methods=['POST', 'GET'])
def register():
    # redirect if logged in
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegistrationForm()

    if form.validate_on_submit():
        user = User(username=form.username.data,
                    email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(_('Registration Success!'))
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', title = 'Register User', form=form)


@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        redirect(url_for('main.index'))
    
    form = ResetPasswordRequestForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash(_('Please check your email for further instructions'))
        return redirect(url_for('auth.login'))
    return render_template('login/reset_password_request.html', form=form, title='Reset Password')

@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('main.index'))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash(_('Password has been reset'))
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)