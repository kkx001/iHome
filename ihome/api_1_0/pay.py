# *_*coding:utf-8 *_*

from . import api
from flask import current_app, jsonify, g, request, session
from ihome.utils.response_code import RET
from ihome.utils.commons import login_required
from ihome.models import Area, House, Facility, HouseImage, User, Order
from ihome import constants, redis_store, db
import json
from ihome.utils.image_storage import storage
from datetime import datetime
from alipay import AliPay
import os


@api.route("/orders/<int:order_id>/payment", methods=["POST"])
@login_required
def order_pay(order_id):
    """发起支付宝支付"""
    user_id = g.user_id

    # 判断订单状态
    try:
        order = Order.query.filter(Order.id == order_id, Order.user_id == user_id,
                                   Order.status == "WAIT_PAYMENT").first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库异常")

    if order is None:
        return jsonify(errno=RET.NODATA, errmsg="订单数据有误")

    app_private_key_string = open(os.path.join(os.path.dirname(__file__), "keys/app_private_key.pem")).read()
    alipy_public_key_string = open(os.path.join(os.path.dirname(__file__), "keys/alipay_public_key.pem")).read()

    app_private_key_string == """
                -----BEGIN RSA PRIVATE KEY-----
                base64 encoded content
                -----END RSA PRIVATE KEY-----
            """

    alipy_public_key_string == """
                -----BEGIN PUBLIC KEY-----
                base64 encoded content
                -----END PUBLIC KEY-----
            """

    # 创建支付宝sdk的工具对象
    alipay_client = AliPay(
        appid="2016092500591407",
        app_notify_url=None,  # 默认回调url
        app_private_key_string=app_private_key_string,  # 自己私钥
        alipay_public_key_string=alipy_public_key_string,  # 支付宝公钥
        sign_type="RSA2",  # RSA或RSA2
        debug=True  # 默认false
    )

    # 手机网站支付，需要跳转到
    # https://openapi.alipaydev.com/gateway.do? + order_string
    order_string = alipay_client.api_alipay_trade_wap_pay(
        out_trade_no=order.id,  # 订单编号
        total_amount=str(order.amount / 100.0),  # 金额
        subject=u"爱家租房 %s" % order.id,  # 订单标题
        return_url="http://127.0.0.1:5000/payComplete.html",  # 返回的链接地址
        notify_url=None,  # 不填则使用默认notify url
    )

    #构建让用户跳转的支付链接
    pay_url = constants.ALIPAY_URL_PREFIX + order_string

    return jsonify(errno=RET.OK, errmsg="OK", data={"pay_url":pay_url})

@api.route("/order/payment", methods=["PUT"])
def save_order_payment_result():
    """保存订单支付结果"""
    alipay_dict = request.form.to_dict()

    # 对支付宝的数据进行分离  提取出支付宝的签名参数sign 和剩下的其他数据
    alipay_sign = alipay_dict.pop("sign")

    app_private_key_string = open(os.path.join(os.path.dirname(__file__), "keys/app_private_key.pem")).read()
    alipy_public_key_string = open(os.path.join(os.path.dirname(__file__), "keys/alipay_public_key.pem")).read()

    app_private_key_string == """
                    -----BEGIN RSA PRIVATE KEY-----
                    base64 encoded content
                    -----END RSA PRIVATE KEY-----
                """

    alipy_public_key_string == """
                    -----BEGIN PUBLIC KEY-----
                    base64 encoded content
                    -----END PUBLIC KEY-----
                """

    # 创建支付宝sdk的工具对象
    alipay_client = AliPay(
        appid="2016092500591407",
        app_notify_url=None,  # 默认回调url
        app_private_key_string=app_private_key_string,  # 自己私钥
        alipay_public_key_string=alipy_public_key_string,  # 支付宝公钥
        sign_type="RSA2",  # RSA或RSA2
        debug=True  # 默认false
    )

    # 借助工具验证参数的合法性
    # 如果确定参数是支付宝的，返回True，否则返回false
    result = alipay_client.verify(alipay_dict, alipay_sign)
    if result:
        # 修改数据库的订单状态信息
        order_id = alipay_dict.get("out_trade_no")
        trade_no = alipay_dict.get("trade_no") #支付宝的交易号

        try:
            Order.query.filter_by(id=order_id).update({"status":"WAIT_COMMENT", "trade_no": trade_no})
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()
    return jsonify(errno=RET.OK, errmsg="OK")