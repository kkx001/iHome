# *_*coding:utf-8 *_*

from flask import Blueprint

# 创建蓝图
api = Blueprint("api_1_0", __name__)

# 导入蓝图
from . import demo, verify_code, passport, profile, houses, orders, pay
