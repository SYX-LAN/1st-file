from flask import render_template,flash,redirect,url_for
from app import app,db
from app.forms import LoginForm, RegistrationForm,EditProfileForm
from app.models import User
from flask_login import current_user, login_user, logout_user, login_required
from flask import request
from werkzeug.urls import url_parse
from datetime import datetime


# initial website
@app.route('/')
@app.route('/index')
@login_required
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
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
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

# <>内容为动态的，URL接受其中username传给视图函数
@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username = username).first_or_404()#没找到就返回404错误
    posts = [
            {'author':user, 'body': 'Test1'},
            {'author':user, 'body': 'Test1'}
            ]
    return render_template('user.html', user = user, posts = posts)

# 下面的装饰器让其他函数执行前都执行这个函数，检查当前用户是否在线，如果在的话把时间修改
@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@app.route('/edit_profile', methods = ['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
#     返回true则把表单数据复制到用户对象然后上传数据库
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
#     false的情况之一，发送的是GET请求，把当前用户数据转移到表单中，确保这些表单的字段具有用户当前的数据
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
#     false另一种情况，表单内容无效，不传递数据
    return render_template('edit_profile.html', title = 'Edit Profile', form = form)
