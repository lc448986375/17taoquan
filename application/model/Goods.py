#encoding=utf-8

from application import db, app
from decimal import Decimal
import time
from marshmallow import Schema, fields
from application.model.GoodsCategory import GoodsCategory
from application.taobao import top
from application.taobao.top.api.rest import TbkTpwdCreateRequest
import traceback

class Goods(db.Model):
    __tablename__ = 'tq_goods'

    __searchable__ = ['goods_name']

    id = db.Column(db.Integer, primary_key = True)
    goods_id = db.Column(db.String, unique = True)
    goods_name = db.Column(db.String, unique = True)
    goods_img_url = db.Column(db.String, unique = True)
    goods_details_url = db.Column(db.String, unique = True)
    goods_category = db.Column(db.String, unique = True)
    taobaoke_url = db.Column(db.String)
    goods_price = db.Column(db.Numeric)
    goods_selled = db.Column(db.Integer)
    goods_shop_name = db.Column(db.String)
    goods_platform = db.Column(db.String)
    goods_coupon = db.Column(db.String)
    goods_coupon_full_amt = db.Column(db.Numeric)
    goods_coupon_amt = db.Column(db.Numeric)
    goods_couponed_price = db.Column(db.Numeric)
    goods_coupon_total = db.Column(db.Integer)
    goods_coupon_balance = db.Column(db.Integer)
    googs_coupon_start_dt = db.Column(db.Integer)
    googs_coupon_end_dt = db.Column(db.Integer)
    googs_coupon_url = db.Column(db.String)
    googs_coupon_buy_url = db.Column(db.String)
    create_dt = db.Column(db.Integer)
    activity_id = db.Column(db.Integer)

    income_ratio = db.Column(db.Numeric) #收入比率
    commission = db.Column(db.Numeric) #佣金

    def __init__(self):
        pass

    def __repr__(self):
        return '<Goods %r,%r,%r>' % (self.goods_id, self.goods_name, self.goods_img_url)

    def convert_amt(slef, amt):
        if amt is None:
            return Decimal('0.00')
        return Decimal(amt).quantize(Decimal('0.00'))
    
    def platform_name(self):
        if self.goods_platform == 'TIANMAO':
            return '天猫'
        elif self.goods_platform == 'TAOBAO':
            return '淘宝'

    def googs_coupon_end_dt_format(self):
        if 99999999 == self.googs_coupon_end_dt:
            return ''
        return time.strftime("%Y-%m-%d", time.strptime(str(self.googs_coupon_end_dt), "%Y%m%d"))

    def fanli_amt(self):
        fanli = self.goods_couponed_price * (self.fanli_rate() * Decimal(0.9) / Decimal(100))
        return Decimal(fanli).quantize(Decimal('0.00'))

    def fanli_rate(self):
        if self.income_ratio is None or self.income_ratio == 0:
            self.income_ratio = 2
        return self.income_ratio

    # 返利后价格
    def rebated_price(self):
        return Decimal(self.goods_couponed_price - self.fanli_amt()).quantize(Decimal('0.00'))
    
    def decimal_to_string(self, decimal_value):
        if decimal_value is None:
            decimal_value = 0
        return str(Decimal(decimal_value).quantize(Decimal('0.00')))

#flask_whooshalchemy.whoosh_index(app, Goods)

class GoodsSchema(Schema):
    id = fields.Int()
    goods_id = fields.Str()
    goods_name = fields.Str()
    goods_img_url = fields.Str()
    goods_details_url = fields.Str()
    goods_category = fields.Str()
    taobaoke_url = fields.Str()
    goods_price = fields.Number()
    goods_selled = fields.Integer()
    goods_shop_name = fields.Str()
    goods_platform = fields.Str()
    goods_coupon = fields.Str()
    goods_coupon_full_amt = fields.Number()
    goods_coupon_amt = fields.Number()
    goods_couponed_price = fields.Number()
    goods_coupon_total = fields.Integer()
    goods_coupon_balance = fields.Integer()
    googs_coupon_start_dt = fields.Integer()
    googs_coupon_end_dt = fields.Integer()
    googs_coupon_url = fields.Str()
    googs_coupon_buy_url = fields.Str()
    create_dt = fields.Integer()
    activity_id = fields.Integer()

    income_ratio = fields.Number() #收入比率
    commission = fields.Number() #佣金

    fanli_amt = fields.Method('get_fanli_amt')
    goods_platform_name = fields.Method('get_goods_platform_name')

    def get_fanli_amt(self, obj):
        return obj.decimal_to_string(obj.fanli_amt())

    def get_goods_platform_name(self, obj):
        return obj.platform_name()

class GoodsDao():

    # 超级返利
    def get_super_fanli(self, count = 4):
        res = db.session.query(Goods).order_by(Goods.income_ratio.desc()).limit(count)
        return res

    # 热卖
    def get_hot_selld(self, count = 4):
        res = db.session.query(Goods).order_by(Goods.goods_selled.desc()).limit(count)
        return res

    # 超级券
    def get_super_coupon(self, count = 4):
        res = db.session.query(Goods).order_by(Goods.goods_coupon_amt.desc()).limit(count)
        return res

    def search(self, key_words = '', page = 1, page_size = 30, **args):
        classes = args.get('classes', '')       # 大分类。两位编码
        cate = args.get('cate', '')             # 明细分类。至少三位编码
        activity = args.get('activity', 0)      # 活动
        order = args.get('order', '') # 排序

        query_temp = None
        
        # 关键词
        if key_words:
            query_temp = Goods.query.msearch(key_words, fields = ['goods_name'])
        else:
            query_temp = db.session.query(Goods)

        # 大分类
        if len(classes) > 0:
            query_temp = query_temp.join(GoodsCategory, Goods.goods_category == GoodsCategory.category_id)
            query_temp = query_temp.filter(GoodsCategory.category_cls == classes)
        # 明细分类
        elif len(cate) > 0:
            query_temp = query_temp.filter(Goods.goods_category.like(cate + '%'))

        # 活动
        if activity > 0:
            query_temp = query_temp.filter(Goods.activity_id == activity)

        # 排序
        if len(order) > 0:
            orders = order.split('_')
            order_by = orders[0]
            order_by_ad = orders[1]

            # 价格排序
            if order_by == 'price':
                if order_by_ad == 'asc':
                    query_temp = query_temp.order_by(Goods.goods_couponed_price.asc())
                elif order_by_ad == 'desc':
                    query_temp = query_temp.order_by(Goods.goods_couponed_price.desc())
            
            # 销量排序
            elif order_by == 'selled':
                if order_by_ad == 'asc':
                    query_temp = query_temp.order_by(Goods.goods_selled.asc())
                elif order_by_ad == 'desc':
                    query_temp = query_temp.order_by(Goods.goods_selled.desc())

            # 返利排序
            elif order_by == 'rebates':
                if order_by_ad == 'asc':
                    query_temp = query_temp.order_by(Goods.income_ratio.asc())
                elif order_by_ad == 'desc':
                    query_temp = query_temp.order_by(Goods.income_ratio.desc())

            # 优惠券金额排序
            elif order_by == 'couponed':
                if order_by_ad == 'asc':
                    query_temp = query_temp.order_by(Goods.goods_coupon_amt.asc())
                elif order_by_ad == 'desc':
                    query_temp = query_temp.order_by(Goods.goods_coupon_amt.desc())


        # 分页
        pagination = query_temp.paginate(
            page, per_page = page_size,
            error_out = False # 页码不存在返回空列表
        )

        return pagination

    def get_by_id(self, id):
        goods = db.session.query(Goods).filter(Goods.id == id).first()
        return goods

    def get_link_goods(self, goods_category, count = 6):
        res = db.session.query(Goods).filter(Goods.goods_category.like(str(goods_category) + '%')).order_by(Goods.goods_selled.desc()).limit(count)
        return res

    def get_tkl_by_url(self, url):
        tkl = None
        try:
            req = TbkTpwdCreateRequest("gw.api.taobao.com", 80)
            req.set_app_info(top.appinfo('24662389', '0a4bc6e525a2e6bd55eb3347cf03bde9'))
            req.text = '17taoquan.wang'
            req.url = url
            resp = req.getResponse()
            app.logger.debug(resp)
            tkl = resp['tbk_tpwd_create_response']['data']['model']

        except Exception as e:
            print(e)
            traceback.print_exc()
            app.logger.error(e)

        return tkl