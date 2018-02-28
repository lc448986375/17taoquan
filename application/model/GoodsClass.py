#encoding=utf-8

from application import db
from marshmallow import Schema, fields

class GoodsClass(db.Model):
    __tablename__ = 'tq_class'

    cls_code = db.Column(db.String, primary_key = True)
    cls_name = db.Column(db.String, unique = True)
    cls_order = db.Column(db.Integer)

    def __init__(self):
        pass

    def __repr__(self):
        return '<GoodsCategory %r,%r>' % (self.category_id, self.category_name)

class GoodsClassSchema(Schema):
    cls_code = fields.Str()
    cls_name = fields.Str()
    cls_order = fields.Int()

class GoodsClassDao():
    def get_cls(self):
        return GoodsClass.query.all()