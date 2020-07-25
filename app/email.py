from flask_mail import Message
from app import mail
from flask import current_app#current_app相当于之前的app，是一个魔法变量，可像全局变量一样工作
from threading import Thread


def send_async_email(app, msg):
#send_async_email()函数中直接使用current_app将不会奏效，因为current_app是一个与处理客户端请求的线程绑定的上下文感知变量。在另一个线程中，current_app没有赋值 我需要做的是访问存储在代理对象中的实际应用程序实例，并将其作为app参数传递。 current_app._get_current_object()表达式从代理对象中提取实际的应用实例，所以它就是我作为参数传递给线程的。
    with app.app_context():
        mail.send(msg)


def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender = sender, recipients = recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target = send_async_email,
           args = (current_app._get_current_object(), msg)).start()
    
    