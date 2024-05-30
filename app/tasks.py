from app import create_app
from app import db
from app.models import Task, User, Post
from rq import get_current_job
import time, json, sys
from app.email import send_email
from flask import render_template

app = create_app()
app.app_context().push()

def _set_task_progess(progress):
    job = get_current_job()
    if job:
        job.meta['progress'] = progress
        job.save_meta()
        task = Task.query.get(job.get_id())
        task.user.add_notification('task_progress', {'task_id':job.get_id(),
                                                     'progress':progress})
        
        if progress >=100:
            task.complete = True
        
        db.session.commit()

def export_posts(user_id):
    try:
        _set_task_progess(0)
        user = User.query.get(user_id)
        i = 0
        data = []
        total_posts = user.post.count()
        for post in user.post.order_by(Post.timestamp.asc()):
            data.append({'body':post.body, 'timestamp':post.timestamp.isoformat()+'z'})
            time.sleep(5)
            i=i+1
            _set_task_progess(100*i//total_posts)
        
        send_email('Your blog posts', 
                   sender=app.config['ADMINS'][0], recipients=[user.email],
                   text_body=render_template("email/export_posts.txt", user=user), 
                   html_body=render_template('email/export_posts.html', user=user),
                   attachments=[('posts.json', 'application/json', json.dumps({'posts':data}, indent=4))], sync=True)                    
    except:
        _set_task_progess(100)
        app.logger.error('Unhandled exception', exc_info=sys.exc_info())
        
    finally:
        _set_task_progess(100)
        
