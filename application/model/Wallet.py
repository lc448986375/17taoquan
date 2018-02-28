#encoding=utf-8

from application import app, db
from sqlalchemy.sql import func
from marshmallow import Schema, fields
from application.model.UserOrders import UserOrders

class WalletDao():
    # 未入账金额
    def get_cf_amt(self, user_id):
        cf_amt = db.session.query(func.sum(UserOrders.rebate_amt)).filter(UserOrders.user_id == user_id).filter(UserOrders.status == 'CF').scalar()

        if cf_amt is None:
            cf_amt = 0

        return float(cf_amt)