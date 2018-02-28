#encoding=utf-8

from application import db

class GoodsCategory(db.Model):
    __tablename__ = 'tq_goods_category'

    id = db.Column(db.Integer, primary_key = True)
    category_id = db.Column(db.String, unique = True)
    category_name = db.Column(db.String, unique = True)
    category_order = db.Column(db.Integer, unique = True)
    category_level = db.Column(db.Integer, unique = True)
    category_parent = db.Column(db.String, unique = True)
    category_cls = db.Column(db.String, unique = True)

    def __init__(self):
        pass

    def __repr__(self):
        return '<GoodsCategory %r,%r>' % (self.category_id, self.category_name)

def category_to_dict(obj):
    return {
        'category_id':obj.category_id,
        'category_name':obj.category_name
    }