from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from app.models import User

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