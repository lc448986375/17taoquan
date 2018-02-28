#encoding=utf-8

from application import app
from application import db
from flask import render_template
from application.model.Goods import Goods, GoodsDao


@app.route('/')
def index():
    site_info = {
        'title':'首页'
    }
    goodsDao = GoodsDao()
    data = {
    	'hot_selled' : goodsDao.get_hot_selld(),
    	'super_coupon' : goodsDao.get_super_coupon(),
        'super_fanli' : goodsDao.get_super_fanli()
    }
    url_args = {
        
    }
    return render_template('index.html', data = data, site_info = site_info, url_args = url_args)

if __name__ == '__main__':
    app.run()
