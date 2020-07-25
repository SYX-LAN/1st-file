from app import db
from app.auth import bp
from flask import render_template,redirect,flash,url_for,request
from werkzeug.urls import url_parse      # url 解析
from app.auth.forms import LoginForm,RegistrationForm,ResetPasswordRequestForm,ResetPasswordForm
from flask_login import current_user,login_user,logout_user# 登陆框有两种情况 一种是已经登陆了 还有一种是要登陆的
from app.models import User,Post  # 对登陆的用户进行一个数据库检索和校验
from app.auth.email import send_password_reset_email


# log in page
@bp.route('/login', methods = ['GET', 'POST'])
def login():
#     current_user可以在任何时刻调用获取用户对象，通过load_user得到这个用户对象
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        
        user = User.query.filter_by(username = form.username.data).first()
        
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))
        
        login_user(user, remember = form.remember_me.data)
        next_page = request.args.get('next')
        
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)
    
    return render_template('auth/login.html', title = 'Sign In', form = form)


# 登出
@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))



@bp.route('/register', methods = ['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegistrationForm()

    #     如果验证通过，获得表单的名称，email数据，同时添加进数据库
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', title = 'Register', form = form)


@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash(
             'Check your email for the instructions to reset your password')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password_request.html',
                           title = 'Reset Password', form = form)

@bp.route('/reset_password/<token>', methods = ['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form = form)