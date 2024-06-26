from app import create_app, db
from app.models import User, Post, Message, Notification, Task, Comment
from flask import request

app = create_app()

# to get into flask shell from terminal
@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Post': Post, 
            'Message': Message, 'Notification': Notification, 
            'Task': Task, 'Comment': Comment  }

if __name__ == "__main__":
    app.run(debug=True)

