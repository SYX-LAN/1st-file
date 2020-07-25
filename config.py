import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
#     邮件服务器信息配置
    MAIL_SERVER = 'smtp.qq.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = True

    MAIL_USERNAME = 'xxx'#邮箱
    MAIL_PASSWORD = 'xxx'#邮箱授权码
    ADMINS = ['xxx']

    
    POSTS_PER_PAGE = 3
