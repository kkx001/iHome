# *_*coding:utf-8 *_*

from werkzeug.routing import BaseConverter
import functools
from flask import session, g, jsonify
from ihome.utils.response_code import RET


#定义正则转换器

class ReCoverter(BaseConverter):
    def __init__(self, url_map, regex):
        #调用父类的初始化方法
        super(ReCoverter, self).__init__(url_map)
        #保存正则表达式
        self.regex = regex



#登陆验证装饰器
def login_required(view_func):
    # wraps函数的作用是将wrapper内层函数的属性
    # 设置为被装饰函数view_func的属性
    @functools.wraps(view_func)
    def wrapper(*args, **kwargs):
        #判断用户的登陆状态
        user_id = session.get("user_id")
        #如果用户是需要登陆的,执行试图函数
        if user_id is not None:
            #将user_id保存到g对象中， 在试图函数中可以通过g对象获取保存的数据
            g.user_id = user_id
            return view_func(*args, **kwargs)
        else:
            #如果未登陆，返回未登陆的信息
            return jsonify(errno=RET.SESSIONERR, errmsg="用户未登陆")

    return wrapper