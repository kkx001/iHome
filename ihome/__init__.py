# *_*coding:utf-8 *_*


from flask import Flask
from config import config_map
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from flask_wtf import CSRFProtect

import redis
import logging
from logging.handlers import RotatingFileHandler
from ihome.utils.commons import ReCoverter


#数据库
db = SQLAlchemy()

#创建redis连接对象
redis_store = None


# 配置日志信息

#设置日志文件等级
logging.basicConfig(level=logging.INFO) #调试info级

# 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
log_file_handler = RotatingFileHandler('logs/log', maxBytes=1024*1024*100, backupCount=10)

#创建日志记录格式                  日志等级         日志信息文件名     行数          日志信息
formatter = logging.Formatter("%(levelname)s  %(filename)s:  %(lineno)d  %(message)s")

#为刚创建的日志记录器设置日志记录格式
log_file_handler.setFormatter(formatter)

#为全局的日志工具对象(flask app 使用的) 添加日志记录器
logging.getLogger().addHandler(log_file_handler)




#工厂模式
def create_app(config_name):
    """
    创建flask应用
    :param config_name: str 配置模式的名字('develop', 'product')
    :return:
    """

    app = Flask(__name__)

    #根据配置模式的名字来获取配置的参数
    config_class = config_map.get(config_name)
    app.config.from_object(config_class)

    #使用app初始化db
    db.init_app(app)

    #初始化redis工具
    global redis_store
    redis_store = redis.StrictRedis(host=config_class.REDIS_HOST, port=config_class.REDIS_PORT)

    #利用flask_session将session保存到redis
    Session(app)

    # 为flask补充csrf防护
    CSRFProtect(app)

    #添加正则转换器
    app.url_map.converters['re'] = ReCoverter

    #注册蓝图
    from ihome import api_1_0
    app.register_blueprint(api_1_0.api, url_prefix="/api/v1.0")

    #注册静态蓝图
    from . import web_html
    app.register_blueprint(web_html.html)

    return app