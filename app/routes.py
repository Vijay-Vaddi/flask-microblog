from app import app
from flask import render_template
from app.forms import LoginForm
@app.route('/')
@app.route('/index')
def index():
    user = {'username':'Vijay-Vaddi'}
    posts =[ 
        {
            'author':{'username':'Vijay-Vaddi'},
            'body':"This is the new beginning"
        },
        {
            'author':{'username':'Obi-Wan Kenobi'},
            'body':"I have failed you Anakin"
        },
    ]
    return render_template("index.html", title='Home', user=user, posts=posts)

@app.route('/login')
def login():
    form = LoginForm()

    if form.validate_on_submit():
        flash(f"Login requested for user {form.username}")
    return render_template('/login.html', title='Log In', form=form)

