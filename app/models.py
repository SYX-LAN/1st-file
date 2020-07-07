from app import db
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(64), index = True, unique = True)
    email = db.Column(db.String(120), index = True, unique = True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref = 'author', lazy = 'dynamic')   
    def __repf__(self): 
        return '<User {}>'.format(self.username)
    
# Post类表示发布的动态， timestamp帮助我们时间索引动态，
# defualt 参数传入datetime.utcnow（这里参数里函数没包含'()'说明传入的不是返回值是函数本身），数据库会将字段自动设置为函数的值,该方法保证任何地方的人都是显示本地时间
# user_id字段被初始化为user.id的外键 这意味着它引用了来自用户表的id值。本处的user是数据库表的名称，flask数据库将小写对应表名 User类有一个新的posts字段，用db.relationship初始化。这不是实际的数据库字段，而是用户和其动态之间关系的高级视图，因此它不在数据库图表中。对于一对多关系，db.relationship字段通常在“一”的这边定义，并用作访问“多”的便捷方式。backref参数定义了代表“多”的类的实例反向调用“一”的时候的属性名称
class Post(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index = True, default = datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    def __repf__(self): 
        return '<Post {}>'.format(self.body)