from app import app

@app.route('/')
@app.route('/index')
def index():
    user = {'username':'Vijay-Vaddi'}
    return '''
<h1> Hi, '''+user['username']+'''
'''