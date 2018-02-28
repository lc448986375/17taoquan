#encoding=utf-8

from flask import render_template, request, redirect, url_for
from application import app, db
from application.model.Goods import GoodsDao
from application.model.GoodsClass import GoodsClassDao
from application.model.GoodsOrder import GoodsOrderDao
from application.taobao import top
from application.taobao.top.api.rest import TbkDgItemCouponGetRequest
import traceback
import re
import json


@app.route('/search', methods = ['GET'])
def search():
	goodsDao = GoodsDao()
	goodsClassDao = GoodsClassDao()
	goodsOrderDao = GoodsOrderDao()

	key_words = request.args.get('kwd', '')
	page = int(request.args.get('page', 1))

	args = {}        
	args['cate'] = str(request.args.get('cate', ''))
	args['order'] = request.args.get('order', '')
	args['activity'] = int(request.args.get('activity', 0))
	args['classes'] = request.args.get('cls', '')

	goodsList = goodsDao.search(key_words, page, 60, **args)
	goodsOrders = goodsOrderDao.get_order()
	for o in goodsOrders:
		if str(args['order']).find(o['order']) >= 0:
			o['selected'] = 'Y'
			if str(args['order']).find('asc') >= 0:
				o['next'] = 'desc'
			else:
				o['next'] = 'asc'
		else:
			o['selected'] = 'N'

	data = {
		'pagination' : goodsList,
		'cls':goodsClassDao.get_cls(),
		'orders':goodsOrders,
		'more_coupon':[]
	}

	url_args = {
		'kwd' : key_words,
		'cur_path' : 'search',
		'cate' : args['cate'],
		'order' : args['order'],
		'activity' : args['activity']
	}
	site_info = {
		'title':'搜索' + url_args['kwd']
	}

	return render_template('list.html', data = data, url_args = url_args, site_info = site_info)

def search_coupon(word, page, page_size):
	req = TbkDgItemCouponGetRequest("gw.api.taobao.com", 80)
	req.set_app_info(top.appinfo('24662389', '0a4bc6e525a2e6bd55eb3347cf03bde9'))

	req.adzone_id = 143546632
	req.platform = 1
	req.page_size = page_size
	req.q = word
	req.page_no = page

	res = {
		'items':[]
	}
	try:
		resp = req.getResponse()
		res['items'] = resp['tbk_dg_item_coupon_get_response']['results']['tbk_coupon']
		res['page'] = {}
		res['page']['page'] = page

		if page > 1:			
			res['page']['has_prev'] = True
			res['page']['prev_num'] = page - 1
		else:
			res['page']['has_prev'] = False

		#if page_size * page <= 100 - page_size:
		if len(res['items']) >= page_size:
			res['page']['has_next'] = True
			res['page']['next_num'] = page + 1
		else:
			res['page']['has_next'] = False

	except Exception as e:
		print(e)
		traceback.print_exc()

	if 'items' in res and res['items'] is not None and len(res['items']) > 0:
		for item in res['items']:
			item['commission_rate'] = round(float(item['commission_rate']) * 0.9, 2)
			item['commission_amt'] = round(float(item['zk_final_price']) * float(item['commission_rate']) / 100, 2)


			# 无优惠券
			if item['coupon_info'] is None or item['coupon_info'] == '无':
				item['coupon_info'] = '购买领返利'
				item['goods_couponed_price'] = round(float(item['zk_final_price']), 2)


			else:
				# 获取满减券
				matchGroups = re.match(r'满([\d\.]+)[元]*减([\d\.]+)[元]*', item['coupon_info'], re.M|re.I)
				if matchGroups is not None:
					groups = matchGroups.groups()
					goods_coupon_full_amt = float(groups[0]) # 满减
					goods_coupon_amt = float(groups[1]) # 优惠券金额
					# 如果满减金额大于商品金额，计算优惠后金额。否则，优惠金额为原价
					if float(item['zk_final_price']) >= goods_coupon_full_amt:
						item['goods_couponed_price'] = round(float(item['zk_final_price']) - goods_coupon_amt, 2)
					else:
						item['goods_couponed_price'] = round(float(item['zk_final_price']), 2)		
					
				# 无条件券
				matchGroups = re.match(r'([\d\.]+)元无条件券', item['coupon_info'], re.M|re.I)
				if matchGroups is not None:
					groups = matchGroups.groups()
					goods_coupon_amt = float(groups[0])
					item['goods_couponed_price'] = round(float(item['zk_final_price']) - goods_coupon_amt, 2)
					

			if float(item['goods_couponed_price']) < 0:
				item['goods_couponed_price'] = 0

	return res

