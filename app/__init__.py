from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
import os
from flask_mail import Mail    
from flask_bootstrap import Bootstrap

app = Flask(__name__)
app.config.from_object(Config)
# 使用@login_required装饰器可以防止匿名用户访问，保护视图函数
login = LoginManager(app)
login.login_view = 'login'
mail = Mail(app)
bootstrap = Bootstrap(app)

# db对象表示数据库, 数据库应用和迁移是一个实例
db = SQLAlchemy(app)
migrate = Migrate(app, db)



# 当不是处于调试状态，且邮箱服务器配置好，才启用电子邮件日志
if not app.debug:
    if app.config['MAIL_SERVER']:
        auth = None
        if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
            auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        secure = None
        if app.config['MAIL_USE_TLS']:
            secure = ()
# 创建SMTPHandler实例，设计处理级别，只有错误和严重信息记录到邮件日志
        mail_handler = SMTPHandler(
            mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
            fromaddr='no-reply@' + app.config['MAIL_SERVER'],
            toaddrs=app.config['ADMINS'], subject='Microblog Failure',
            credentials=auth, secure=secure)
        mail_handler.setLevel(logging.ERROR)
# 然后附加到app.logger中
        app.logger.addHandler(mail_handler)
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/microblog.log', maxBytes = 10240, backupCount = 10)
#   记录消息为时间戳，记录级别，消息，源代码文件和行号
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    
    app.logger.setLevel(logging.INFO)
    app.logger.info('Microblog Startup')

from app import routes, models, errors# models用来定义数据库结构,这句话要放在最底部，因为在microblog里我们导入了app,我们执行这个__init__模块，此处导入routes模块，在routes模块中又导入了app，重新回到这个模块执行这里的代码，如果把这句话放在上端，会导致再跳回routes模块循环导入。