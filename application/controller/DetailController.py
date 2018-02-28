#encoding=utf-8

from application.model.Goods import Goods, GoodsSchema, GoodsDao
from application import app, db
from flask import render_template, request
from application.taobao.top.api.rest import TbkTpwdCreateRequest, TbkItemRecommendGetRequest, TbkDgItemCouponGetRequest
from application.taobao import top
import traceback
import json

@app.route('/show/<int:id>')
def show(id):
    goodsDao = GoodsDao()
    goods = goodsDao.get_by_id(id)
    if goods is not None:
        data = {
            'goods' : goods,
            'link_goods' : goodsDao.get_link_goods(goods.goods_category)
        }
        site_info = {
            'title' : goods.goods_name
        }
        url_args = {
            
        }
        return render_template('show.html', data = data, site_info = site_info, url_args = url_args)
        
    else:
        site_info = {
            'title' : '优惠券抢完了, 为您推荐更多优惠券'
        }
        url_args = {
            
        }
        return render_template('show.html', data = None, site_info = site_info, url_args = url_args)

@app.route('/get_taokouling', methods=['GET', 'POST'])
def get_taokouling():
    goodsDao = GoodsDao()
    try:
        if request.method == 'POST':
            id = request.form.get('id')
        else:
            id = request.args.get('id')
            
        goods = goodsDao.get_by_id(id)
        tkl = goodsDao.get_tkl_by_url(goods.googs_coupon_buy_url)

        msg = "[" + goods.goods_name + "]\n复制这条信息, " + tkl + ", 打开手机淘宝, 即可在手机淘宝中领券购买. 来自[一起淘券网(17taoquan.wang)]优惠分享"
        res = {"success":True, "data":{"toukouling":msg}}

        if request.method == 'GET':
            callback = request.args.get('callback', '')
            return '{0}({1})'.format(callback, json.dumps(res))

        else:
            return json.dumps(res)

    except Exception as e:
        print(e)
        traceback.print_exc()
        app.logger.error(e)
        return '淘口令生成失败, 请稍后重试'


@app.route('/get_taokouling_by_url', methods=['GET', 'POST'])
def get_taokouling_by_url():
    try:
        if request.method == 'POST':
            url = request.form.get('url')
            name = request.form.get('name', '')
        else:
            url = request.args.get('url')
            name = request.args.get('name', '')
            
        
        req = TbkTpwdCreateRequest("gw.api.taobao.com", 80)
        req.set_app_info(top.appinfo('24662389', '0a4bc6e525a2e6bd55eb3347cf03bde9'))
        req.text = name + "来自[一起淘券网(17taoquan.wang)]优惠分享"
        req.url = url
        resp = req.getResponse()
        tkl = resp['tbk_tpwd_create_response']['data']['model']
        msg = "[" + name + "]\n复制这条信息, " + tkl + ", 打开手机淘宝, 即可在手机淘宝中领券购买. 来自[一起淘券网(17taoquan.wang)]优惠分享"
        res = {"success":True, "data":{"toukouling":msg}}
        return json.dumps(res)
    except Exception as e:
        print(e)
        traceback.print_exc()
        app.logger.error(e)
        return '淘口令生成失败, 请稍后重试'

   
@app.route('/wx_api/show/<int:id>', methods=['GET', 'POST'])
def wx_api_show(id):
    goods = db.session.query(Goods).filter(Goods.id == id).first()
    res = None
    if goods is not None:
        res = {'success':True}
        data = {
            'goods' : goods_to_dict(goods),
            'link_goods' : []
        }
        linkGoods = get_link_goods(goods.goods_category, 4)
        data['link_goods'] = [goods_to_dict(o) for o in linkGoods]
        res['data'] = data
    else:
        res = {'success':False, 'msg':'商品不存在'}

    if request.method == 'GET':
        callback = request.args.get('callback', '')
        return '{0}({1})'.format(callback, json.dumps(res))

    else:
        return json.dumps(res)


'''
@app.route('/get_link_goods', methods=['POST'])
def get_link_goods():
    try:
        if request.method == 'POST':
            goods_category = request.form.get('goods_category')
            res = db.session.query(Goods).order_by(Goods.goods_selled.desc()).limit(6)
            data = {"success":True, "data" : res}
            return json.dumps(data)
    except Exception as e:
        print(e)
        traceback.print_exc()
        #return '淘口令生成失败, 请稍后重试'
'''
'''
@app.route('/get_haoquangou_goods', methods=['POST'])
def get_haoquangou_goods():
    try:
        if request.method == 'POST':
            adzone_id = 143546632
            
            req = TbkDgItemCouponGetRequest("gw.api.taobao.com", 80)
            req.set_app_info(top.appinfo('24662389', '0a4bc6e525a2e6bd55eb3347cf03bde9'))
            
            req.adzone_id = adzone_id
            req.platform = 1
            #req.cat = "16,18"
            #req.page_size = 10
            #req.q = "女装"
            req.page_no = 1

            resp = req.getResponse()
            item_list = resp['tbk_dg_item_coupon_get_response']['results']['tbk_coupon']
            res = {"success":True, "data":item_list}
            return json.dumps(res)
    except Exception as e:
        print(e)
        traceback.print_exc()
        #return '淘口令生成失败, 请稍后重试'
'''

'''
@app.route('/get_link_goods', methods=['POST'])
def get_link_goods():
    try:
        if request.method == 'POST':
            goods_id = request.form.get('goods_id')
            
            req = TbkItemRecommendGetRequest("gw.api.taobao.com", 80)
            req.set_app_info(top.appinfo('24662389', '0a4bc6e525a2e6bd55eb3347cf03bde9'))
            req.fields = "num_iid,title,pict_url,small_images,reserve_price,zk_final_price,user_type,provcity,item_url"
            req.num_iid = int(goods_id)
            req.count = 10
            req.platform = 1
            resp = req.getResponse()
            item_list = resp['tbk_item_recommend_get_response']['results']['n_tbk_item']
            res = {"success":True, "data":item_list}
            return json.dumps(res)
    except Exception as e:
        print(e)
        traceback.print_exc()
        return '淘口令生成失败, 请稍后重试'
'''