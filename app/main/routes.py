from flask import render_template,flash,redirect,url_for,current_app,request
from app import db
from app.models import User,Post
from flask_login import current_user, login_required
from datetime import datetime
from app.main.forms import EditProfileForm,PostForm
from app.main import bp

# 下面的装饰器让其他函数执行前都执行这个函数，检查当前用户是否在线，如果在的话把时间修改
@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

# initial website
@bp.route('/', methods = ['GET', 'POST'])
@bp.route('/index', methods = ['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body = form.post.data, author = current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post is now live!')

        # 重定向的原因https://en.wikipedia.org/wiki/Post/Redirect/Get
        return redirect(url_for('main.index'))

    # 参数1：从1开始的页码
    # 参数2：每页的数据量
    # 参数3：错误处理布尔标记，如果是True，当请求范围超出已知范围时自动引发404错误。如果是False，则会返回一个空列表。
    # 得到一个对象，items可得到数据
    # page从URL中获得，否则默认为1
    page = request.args.get('page', 1, type = int)
    posts = current_user.followed_posts().paginate(page, current_app.config['POSTS_PER_PAGE'], False)
    
    next_url = url_for('main.index', page = posts.next_num) \
        if posts.has_next else None
    
    prev_url = url_for('main.index', page = posts.prev_num) \
        if posts.has_prev else None
    
    return render_template('index.html', title = 'Home Page', 
                           form = form, posts = posts.items
                          ,next_url = next_url, prev_url = prev_url)

@bp.route('/explore')
@login_required
def explore():
    
    page = request.args.get('page', 1, type = int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(page, current_app.config['POSTS_PER_PAGE'], False)
    
    next_url = url_for('main.explore', page = posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.explore', page = posts.prev_num) \
        if posts.has_prev else None
    
    return render_template('index.html', title = 'Explore', posts = posts.items, next_url = next_url, prev_url = prev_url)



@bp.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username = username).first_or_404()
    page = request.args.get('page', 1, type = int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.user', username = user.username,
                       page = posts.next_num) if posts.has_next else None
    prev_url = url_for('main.user', username = user.username,
                       page = posts.prev_num) if posts.has_prev else None
    return render_template('user.html', user = user, posts = posts.items,
                           next_url = next_url, prev_url = prev_url)





@bp.route('/edit_profile', methods = ['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)

    #     返回true则把表单数据复制到用户对象然后上传数据库
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('main.edit_profile'))

    #     false的情况之一，发送的是GET请求，把当前用户数据转移到表单中，确保这些表单的字段具有用户当前的数据
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me

        #     false另一种情况，表单内容无效，不传递数据
    return render_template('edit_profile.html', title = 'Edit Profile', form = form)

@bp.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username = username).first()
    
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('main.index'))
    
    if user == current_user:
        flash('You cannot follow yourself!')
        return redirect(url_for('main.user', username = username))
    
    current_user.follow(user)
    db.session.commit()
    flash('You are following {}!'.format(username))
    
    return redirect(url_for('main.user', username = username))

@bp.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username = username).first()
    
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('main.index'))
    
    if user == current_user:
        flash('You cannot unfollow yourself!')
        return redirect(url_for('main.user', username = username))
    
    current_user.unfollow(user)
    db.session.commit()
    flash('You are not following {}.'.format(username))
    return redirect(url_for('main.user', username = username))

