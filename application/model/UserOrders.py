#encoding=utf-8

from application import app, db
from marshmallow import Schema, fields
import time

class UserOrders(db.Model):
    __tablename__ = 'tq_user_orders'

    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.String, unique = True)
    status = db.Column(db.String, unique = True)
    mall_orders_id = db.Column(db.String, unique = True)
    orders_amt = db.Column(db.Numeric, unique = True)
    rebate_amt = db.Column(db.Numeric)
    submit_dt = db.Column(db.Integer, unique = True)
    confirm_dt = db.Column(db.Integer)
    complete_dt = db.Column(db.Integer)
    error_msg =  db.Column(db.String)

    def __init__(self):
        pass

    def __repr__(self):
        return '<UserOrders %r, %r>' % (self.id, self.mall_orders_id)


class UserOrdersSchema(Schema):
    id = fields.Int()
    user_id = fields.Str()
    status = fields.Str()
    mall_orders_id = fields.Str()
    orders_amt = fields.Int()
    rebate_amt = fields.Number()
    submit_dt = fields.Int()
    confirm_dt = fields.Int()
    complete_dt = fields.Int()
    error_msg = fields.Str()

    status_nm = fields.Method('get_status_nm')

    def get_status_nm(self, obj):
        if obj.status == 'SB':
            return '已提交'
        elif obj.status == 'CF':
            return '已确认'
        elif obj.status == 'CM':
            return '已完成'
        elif obj.status == 'ER':
            return '错误订单'
        else:
            return ''

class UserOrdersDao():
    def add(self, user_id, mall_orders_id):
        orders = UserOrders()
        orders.user_id = user_id
        orders.mall_orders_id = mall_orders_id
        orders.submit_dt = time.strftime('%Y%m%d%H%M%S', time.localtime())
        orders.status = 'SB'
        orders.orders_amt = 0
        orders.rebate_amt = 0
        db.session.add(orders)
        db.session.commit()

    def get_orders_by_user(self, user_id):
        return db.session.query(UserOrders).filter(UserOrders.user_id == user_id).order_by(UserOrders.submit_dt.desc()).all()