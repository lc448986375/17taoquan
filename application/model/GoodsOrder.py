#encoding=utf-8

class GoodsOrderDao():
    def get_order(self):
        res = [
            {'order' : 'price', 'order_name' : '价格', 'cur':'', 'next':'asc'},
            {'order' : 'selled', 'order_name' : '销量', 'cur':'', 'next':'desc'},
            #{'order' : 'rebates', 'order_name' : '返利', 'cur':'', 'next':'desc'}
            {'order' : 'couponed', 'order_name' : '优惠券金额', 'cur':'', 'next':'desc'}
        ]
        return res