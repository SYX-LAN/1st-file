from flask import Blueprint

# 创建Blueprint类，设置了模块名称
bp = Blueprint('errors', __name__)

# 底层导入，防止循环导入
from app.errors import handlers