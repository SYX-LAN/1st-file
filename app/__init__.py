from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

app = Flask(__name__)
app.config.from_object(Config)
# 使用@login_required装饰器可以防止匿名用户访问，保护视图函数
login = LoginManager(app)
login.login_view = 'login'

# db对象表示数据库, 数据库应用和迁移是一个实例
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# models用来定义数据库结构
from app import routes,models
