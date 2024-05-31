# handles uploading user post and profile pictures 
import os 
from flask import current_app
from PIL import Image
from flask_login import current_user

def add_pic(pic_upload, post=None):
    filename = pic_upload.filename
    extension = filename.split('.')[-1]

    img = Image.open(pic_upload)

    if post:
        # if called from post, mk username dir, save with post id
        saved_name = str(post.author.username)+str(post.id) +'.'+extension
        userdir = os.path.join(current_app.config['POSTS_FOLDER'], post.author.username)
        os.makedirs(userdir, exist_ok=True)
        file_path = os.path.join(userdir,saved_name)
        img = img.convert("RGB")
    else:
        # else save in prof pic folder
        saved_name = str(current_user.username)+'.'+extension
        file_path = os.path.join(current_app.config['PROFILE_PIC_FOLDER'], 
                             saved_name)
        output_size = (150,150)
        img.thumbnail(output_size)

    img.save(file_path)

    return saved_name