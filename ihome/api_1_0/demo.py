# *_*coding:utf-8 *_*

from . import api

@api.route("/")
def index():
    return "hello flask"