from flask import render_template,flash,redirect,url_for
from app import app,db
from app.forms import LoginForm, RegistrationForm
from app.models import User
from flask_login import current_user, login_user, logout_user
from flask import request
from werkzeug.urls import url_parse

# initial website
@app.route('/')
@app.route('/index')
def index():
    posts = [
        {
            'author': {'username': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'username': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        }
    ]
    return render_template('index.html', title = 'Home', posts = posts)


# log in page
@app.route('/login', methods = ['GET', 'POST'])
def login():
#     current_user可以在任何时刻调用获取用户对象，通过load_user得到这个用户对象
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
#filter_by()可以得到一个只包含具有匹配用户名的对象的查询结果集，first()用来完成查询，存在则返回用户对象，all()返回匹配的所有结果
        user = User.query.filter_by(username = form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
#       账号密码正确则把登录注册状态改变为已登录，并把实例赋值给current_user
        login_user(user, remember = form.remember_me.data)
        return redirect(url_for('index'))
    return render_template('login.html', title = 'Sign In', form = form)
# 登出
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods = ['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
#     如果验证通过，获得表单的名称，email数据，同时添加进数据库
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)