# *_*coding:utf-8 *_*

from . import db

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

from ihome import constants


class BaseModel:
    """模型基类,为每个模型补充创建时间和更新时间"""
    # 记录创建时间
    create_time = db.Column(db.DateTime, default=datetime.now)

    # 记录更新时间
    update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)


class User(BaseModel, db.Model):
    """用户"""
    __tablename__ = "ih_user"
    id = db.Column(db.Integer, primary_key=True)  # 用户ID
    name = db.Column(db.String(32), unique=True, nullable=False)  # 用户昵称,不能为空
    password_hash = db.Column(db.String(128), nullable=False)  # 用户密码,不能为空
    mobile = db.Column(db.String(11), unique=True, nullable=False)  # 手机号
    real_name = db.Column(db.String(32))  # 真是姓名
    id_card = db.Column(db.String(20))  # 身份证号
    avatar_url = db.Column(db.String(128))  # 用户图像路径
    houses = db.relationship("House", backref='user')  # 用户发布的房屋
    order = db.relationship("Order", backref='user')  # 用户的订单

    # 加上property装饰器后，会把函数变为属性，属性名即为函数名
    @property
    def password(self):
        """读取属性的函数行为"""
        return AttributeError("这个属性只能设置，不能读取")

    # 使用这个装饰器, 对应设置属性操作
    @password.setter
    def password(self, value):
        """
        设置属性 user.password="xxx"
        :param value: 设置属性时的数据 value就是"xxxxx", 原始的明文密码
        :return:
        """
        # 对密码进行加密
        self.password_hash = generate_password_hash(value)

    def check_password(self, passwd):
        """
        检验密码正确性
        :param passwd: 用户登录填写的原始密码
        :return: 如果正确，返回True， 否则返回False
        """
        return check_password_hash(self.password_hash, passwd)

    def to_dict(self):
        """将对象转换为字典数据"""
        user_dict = {
            "user_id": self.id,
            "name": self.name,
            "mobile": self.mobile,
            "avatar": constants.QINIU_URL_DOMAIN + self.avatar_url if self.avatar_url else "",
            "create_time": self.create_time.strftime("%Y-%m-%d  %H:%M:%S")
        }
        return user_dict

    def auth_to_dict(self):
        """将实名信息转换为字典数据"""
        auth_dict = {
            "user_id": self.id,
            "real_name": self.real_name,
            "id_card": self.id_card
        }
        return auth_dict


class Area(BaseModel, db.Model):
    """城区"""
    __tablename__ = "ih_area"
    id = db.Column(db.Integer, primary_key=True)  # 区域编号
    name = db.Column(db.String(32), nullable=False)  # 城区名字，不能为空
    houses = db.relationship("House", backref="area")  # 区域内的房屋

    def to_dict(self):
        """将对象转换为字典"""
        d = {
            "aid": self.id,
            "aname": self.name
        }
        return d


# 房屋设施表， 建立房屋与设施的多对多关系
house_facility = db.Table(
    "ih_house_facility",
    db.Column("house_id", db.Integer, db.ForeignKey("ih_house.id"), primary_key=True),  # 房屋编号
    db.Column("facility_if", db.Integer, db.ForeignKey("ih_facility.id"), primary_key=True)  # 设施编号
)


class House(BaseModel, db.Model):
    """房屋"""
    __tablename__ = "ih_house"
    id = db.Column(db.Integer, primary_key=True)  # 房屋编号
    user_id = db.Column(db.Integer, db.ForeignKey('ih_user.id'), nullable=False)  # 房屋主人的编号
    area_id = db.Column(db.Integer, db.ForeignKey('ih_area.id'), nullable=False)  # 归属地编号
    title = db.Column(db.String(64), nullable=False)  # 标题
    price = db.Column(db.Integer, default=0)  # 价格 单位:元
    address = db.Column(db.String(512), default="")  # 地址
    room_count = db.Column(db.Integer, default=1)  # 房间数
    acreage = db.Column(db.Integer, default=0)  # 房屋面积
    unit = db.Column(db.String(32), default="")  # 房屋单元
    capacity = db.Column(db.Integer, default=1)  # 房间容纳的人数
    beds = db.Column(db.String(64), default="")  # 房间床铺的配置
    deposit = db.Column(db.Integer, default=0)  # 房屋押金
    min_days = db.Column(db.Integer, default=1)  # 最少入住天数
    max_days = db.Column(db.Integer, default=0)  # 最多入住天数
    order_count = db.Column(db.Integer, default=0)  # 预定完成的该房屋的订单数
    index_image_url = db.Column(db.String(256), default="")  # 房屋图片的路径
    facilities = db.relationship("Facility", secondary=house_facility)  # 房屋设施
    images = db.relationship("HouseImage")  # 房屋图片
    orders = db.relationship("Order", backref='house')  # 房屋的订单

    def to_basic_dict(self):
        """将基本信息转换为字典数据"""
        house_dict = {
            "house_id": self.id,
            "title": self.title,
            "price": self.price,
            "area_name": self.area.name,
            "img_url": constants.QINIU_URL_DOMAIN + self.index_image_url if self.index_image_url else "",
            "room_count": self.room_count,
            "order_count": self.order_count,
            "address": self.address,
            "user_avatar": constants.QINIU_URL_DOMAIN + self.user.avatar_url if self.user.avatar_url else "",
            "ctime": self.create_time.strftime("%Y-%m-%d")
        }
        return house_dict

    def to_full_dict(self):
        """将详细信息转换为字典数据"""
        house_dict = {
            "hid": self.id,
            "user_id": self.user_id,
            "user_name": self.user.name,
            "user_avatar": constants.QINIU_URL_DOMAIN + self.user.avatar_url if self.user.avatar_url else "",
            "title": self.title,
            "price": self.price,
            "address": self.address,
            "room_count": self.room_count,
            "acreage": self.acreage,
            "unit": self.unit,
            "capacity": self.capacity,
            "beds": self.beds,
            "deposit": self.deposit,
            "min_days": self.min_days,
            "max_days": self.max_days,
        }

        # 房屋图片
        img_urls = []
        for image in self.images:
            img_urls.append(constants.QINIU_URL_DOMAIN + image.url)
        house_dict["img_urls"] = img_urls

        # 房屋设施
        facilities = []
        for facility in self.facilities:
            facilities.append(facility.id)
        house_dict["facilities"] = facilities

        # 评论信息
        comments = []
        orders = Order.query.filter(Order.house_id == self.id, Order.status == "COMPLETE", Order.comment != None) \
            .order_by(Order.update_time.desc()).limit(constants.HOUSE_DETAIL_COMMENT_DISPLAY_COUNTS)
        for order in orders:
            comment = {
                "comment": order.comment,  # 评论的内容
                "user_name": order.user.name if order.user.name != order.user.mobile else "匿名用户",  # 发表评论的用户
                "ctime": order.update_time.strftime("%Y-%m-%d %H:%M:%S")  # 评价的时间
            }
            comments.append(comment)
        house_dict["comments"] = comments
        return house_dict


class Facility(BaseModel, db.Model):
    """设施信息"""
    __tablename__ = "ih_facility"
    id = db.Column(db.Integer, primary_key=True)  # 设施id
    name = db.Column(db.String(32), nullable=False)  # 设施名字， 不能为空


class HouseImage(BaseModel, db.Model):
    """房屋图片"""
    __tablename__ = "ih_house_image"
    id = db.Column(db.Integer, primary_key=True)  # 房屋图片id
    house_id = db.Column(db.Integer, db.ForeignKey("ih_house.id"), nullable=False)  # 房屋ID
    url = db.Column(db.String(256), nullable=False)  # 图片路径


class Order(BaseModel, db.Model):
    """订单"""
    __tablename__ = "ih_order"
    id = db.Column(db.Integer, primary_key=True)  # 订单ID
    user_id = db.Column(db.Integer, db.ForeignKey("ih_user.id"), nullable=False)  # 下订单的用户编号
    house_id = db.Column(db.Integer, db.ForeignKey("ih_house.id"), nullable=False)  # 预定的房间编号
    begin_date = db.Column(db.DateTime, nullable=False)  # 订单开始时间
    end_date = db.Column(db.DateTime, nullable=False)  # 订单结束时间
    days = db.Column(db.Integer, nullable=False)  # 预定天数
    house_price = db.Column(db.Integer, nullable=False)  # 预定单价
    amount = db.Column(db.Integer, nullable=False)  # 订单总价
    status = db.Column(  # 订单状态
        db.Enum(
            "WAI_ACCEPT",  # 待接单
            "WAIT_PAYMENT",  # 待支付
            "PAID",  # 已支付
            "WAIT_COMMENT",  # 待评价
            "COMPLETE",  # 已完成
            "CANCELED",  # 已取消
            "REJECTED",  # 已拒单
        ), default='WAIT_ACCEPT', index=True)
    comment = db.Column(db.Text)  # 订单评价或拒单原因
    trade_no = db.Column(db.String(100))  # 交易流水号

    def to_dict(self):
        """将订单信息转换为字典数据"""
        order_dict = {
            "order_id": self.id,
            "title": self.house.title,
            "img_url": constants.QINIU_URL_DOMAIN + self.house.index_image_url if self.house.index_image_url else "",
            "start_date": self.begin_date.strftime("%Y-%m-%d"),
            "end_date": self.end_date.strftime("%Y-%m-%d"),
            "ctime": self.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            "days": self.days,
            "amount": self.amount,
            "status": self.status,
            "comment": self.comment if self.comment else ""
        }
        return order_dict
