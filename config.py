import os 
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'super-secret-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///'+os.path.join(basedir,'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = 'smtp.googlemail.com' or os.environ.get('MAIL_SERVER')
    MAIL_PORT = 587 or int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = 1 or os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = '' or os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = '' or os.environ.get('MAIL_PASSWORD') 
    ADMINS = ['vijayzvaddi@gmail.com']
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')
    POSTS_PER_PAGE = 5
    LANGUAGES = ['en', 'es']
    MS_TRANSLATOR_KEY = '' or os.environ.get('MS_TRANSLATOR_KEY')  
    ELASTICSEARCH_URL=os.environ.get('ELASTICSEARCH_URL')
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://'
    POSTS_FOLDER= os.path.join(basedir,'app/static/posts_images')
    PROFILE_PIC_FOLDER=os.path.join(basedir,'app/static/profile_pictures')

