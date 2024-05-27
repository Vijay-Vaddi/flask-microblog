# handles uploading user profile picture
import os 
from flask import current_app
from PIL import Image

def add_profile_pic(pic_upload, username):
    filename = pic_upload.filename
    extension = filename.split('.')[-1]
    saved_name = str(username)+'.'+extension

    file_path = os.path.join(current_app.root_path, 'static/profile_pictures', 
                             saved_name)
    
    output_size = (150,150)

    img = Image.open(pic_upload)
    img.thumbnail(output_size)
    img.save(file_path)

    return saved_name