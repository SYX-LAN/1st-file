from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from app.models import User
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import Length

class EditProfileForm(FlaskForm):
    username = StringField('Username', validators = [DataRequired()])
    about_me = TextAreaField('About Me', validators = [Length(min = 0, max = 140)])#输入字符长度在0-140之间
    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username
        
    def validate_username(self,username):
        if username.data != self.original_username:
            user = User.query.filter_by(username = self.username.data).first()
            if user is not None:
                raise ValidationError('Please Use Different Username.')
        

class LoginForm(FlaskForm):
    username = StringField('Username', validators = [DataRequired()])
    password = PasswordField('Password', validators = [DataRequired()])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Sign In')
    
# 注册表单
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators = [DataRequired()])
    email = StringField('Email', validators = [DataRequired(), Email()])#Email()验证器保证输入的邮件格式正确
    password = PasswordField('Password', validators = [DataRequired()])
    password2 = PasswordField('Repeat Password', validators = [DataRequired(), EqualTo('password')])#重新输入密码验证
    submit = SubmitField('Submit')
    
#     验证用户名和邮箱唯一
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class PostForm(FlaskForm):
    post = TextAreaField('Say Something', validators = [DataRequired(), Length(min = 1,max = 140)])
    submit = SubmitField('Submit')

    
class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Your E-mail', validators = [DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')
    
class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators = [DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators = [DataRequired(), EqualTo('password')])
    submit = SubmitField('Request Password Reset')
