from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5
from time import time
import jwt
from app import app,db,login


# 表内的2个实例都是关联到同一个类，被称为自引用表，这里没和user，posts表一样声明成模型  因为这是一个除了外键没有其他数据的辅助表，所以我创建它的时候没有关联到模型类。

followers = db.Table(
    'followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)


class User(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
# User关联到User，secondary指定关联表为上面定义的followers
# primaryjoin 指明了通过关系表关联到左侧实体（关注者）的条件 。关系中的左侧的join条件是关系表中的follower_id字段与这个关注者的用户ID匹配。followers.c.follower_id表达式引用了该关系表中的follower_id列。
# secondaryjoin 指明了通过关系表关联到右侧实体（被关注者）的条件 。 这个条件与primaryjoin类似，唯一的区别在于，现在我使用关系表的字段的是followed_id了。
# backref定义了右侧实体如何访问该关系。在左侧，关系被命名为followed，所以在右侧我将使用followers来表示所有左侧用户的列表，即粉丝列表。附加的lazy参数表示这个查询的执行模式，设置为动态模式的查询不会立即执行，直到被调用，这也是我设置用户动态一对多的关系的方式。
# lazy和backref中的lazy类似，只不过当前的这个是应用于左侧实体，backref中的是应用于右侧实体
    
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

#   重用append和remove方法，is_following来确认操作两者当前关系是否成立,self.followed即为followed数据库
    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)
#     filter不同于filter_by只能检查是否等于一个常量值，这里的过滤条件为查找关联表中左侧外键设置为self用户且右侧设置为user参数的数据行。 查询以count()方法结束，返回结果的数量。 这个查询的结果是0或1
    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0
    
    
    def followed_posts(self):
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)).filter(
                followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Post.timestamp.desc())

    
    def avatar(self,size):
#         size来指定大小，digest指定图片，d产生随机图片
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

# 生成密码哈希值
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
#   校对密码是否正确
    def check_password(self, password):   
        return check_password_hash(self.password_hash, password)
    
#     以字符串形式生成一个令牌
    def get_reset_password_token(self, expires_in = 600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm = 'HS256').decode('utf-8')
    
    
    #静态方法可以直接从类外调用     
    @staticmethod
    def verify_reset_password_token(token):
        try:
            #解码该token，过期或者出错就引发异常             
            id = jwt.decode(token, app.config['SECRET_KEY'], algorithms = ['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)
        
        
        
    def __repr__(self):
        return '<User {}>'.format(self.username)    

@login.user_loader
def load_user(id):
    return User.query.get(int(id))


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