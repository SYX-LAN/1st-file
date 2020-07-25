from flask import Flask, request,current_app
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
import os
from flask_mail import Mail    
from flask_bootstrap import Bootstrap
from flask_moment import Moment





# 使用@login_required装饰器可以防止匿名用户访问，保护视图函数
login = LoginManager()
login.login_view = 'auth.login'
login.login_message = '请登录'
mail = Mail()
bootstrap = Bootstrap()
# Flask-Moment与moment.js一起工作，因此应用的所有模板都必须包含moment.js。为了确保该库始终可用，我将把它添加到基础模板中，可以通过两种方式完成。 最直接的方法是显式添加一个<script>标签来引入库，但Flask-Moment的moment.include_moment()函数可以更容易地实现它，它直接生成了一个<script>标签并在其中包含moment.js：
moment = Moment()
# db对象表示数据库, 数据库应用和迁移是一个实例
db = SQLAlchemy()
migrate = Migrate()


def create_app(config_class = Config):
    app = Flask(__name__,template_folder='templates')
    app.config.from_object(config_class)
    
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    mail.init_app(app)
    bootstrap.init_app(app)
    moment.init_app(app)

    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from app.auth import bp as auth_bp
        # 此蓝图中的路由都有一个'/auth'前缀
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)
        

    # 当不是处于调试状态，且邮箱服务器配置好，才启用电子邮件日志
    if not app.debug and not app.testing:
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
        
        return app

from app import models
