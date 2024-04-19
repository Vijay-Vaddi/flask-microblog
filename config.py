import os 

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'super-secret-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI') or \
        'sqlite:///'+os.path.join(basedir,'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = 'smtp.googlemail.com' or os.environ.get('MAIL_SERVER')
    MAIL_PORT = 587 or int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = 1 or os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = 'vijayzvaddi@gmail.com' or os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = 'ou---------h' or os.environ.get('MAIL_PASSWORD')
    ADMINS = ['vijayzvaddi@gmail.com']
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')
    POSTS_PER_PAGE = 3


