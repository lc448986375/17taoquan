#encoding=utf-8

from application import app
from application import db
from flask import render_template, request
from application.model.Goods import Goods
from application.model.GoodsCategory import GoodsCategory
from sqlalchemy.sql import func
from sqlalchemy import distinct
import xlrd
import re
import time
import traceback
import threading

#执行导入
@app.route('/import_excel', methods=['GET'])
def import_excel():
	try:
		key = request.args['key']
		dt = request.args['dt']
		start_num = int(request.args['start'])
		if key == '6666666':
			data = xlrd.open_workbook('application/data/' + dt + '.xls')
			table = data.sheets()[0]
			nrows = table.nrows #行数
			
			thr = threading.Thread(target = sync_import, args = [app, table, start_num])#创建线程
			thr.start()

			return render_template('error.html', error_msg = '正在执行:' + str(nrows - 1) + '条')
		else:
			return render_template('error.html', error_msg = 'key error')
	except Exception as e:
		print(e)
		traceback.print_exc()
		return render_template('error.html', error_msg = 'no key' + str(e))

@app.route('/delete_end_dt', methods=['GET'])
def delete_end_dt():
	try:
		key = request.args['key']
		dt = request.args['dt']
		page_size = 500
		if key == '6666666':
			pagination = db.session.query(Goods).filter('googs_coupon_end_dt < ' + dt).paginate(
				1, per_page = page_size,
	    		error_out = False # 页码不存在返回空列表
			)
			thr = threading.Thread(target = sync_delete, args = [app, pagination.items])#创建线程
			thr.start()

			return render_template('error.html', error_msg = '正在删除:' + str(page_size) + '/' + str(pagination.total) + '条')
		else:
			return render_template('error.html', error_msg = 'key error')
	except Exception as e:
		print(e)
		traceback.print_exc()
		return render_template('error.html', error_msg = 'no key' + str(e))

@app.route('/delete_by_activity', methods=['GET'])
def delete_by_activity():
	key = request.args.get('key', None)
	activity_id = request.args.get('activity_id', 0)
	page_size = 500
	if key == '6666666':
		if activity_id == 0:
			return render_template('error.html', error_msg = 'activity_id must not zero')
		else:
			pagination = db.session.query(Goods).filter('activity_id = ' + activity_id).paginate(
				1, per_page = page_size,
	    		error_out = False # 页码不存在返回空列表
			)
			thr = threading.Thread(target = sync_delete, args = [app, pagination.items])#创建线程
			thr.start()

			return render_template('error.html', error_msg = '正在删除:' + str(page_size) + '/' + str(pagination.total) + '条')

	else:
		return render_template('error.html', error_msg = 'key error')


@app.route('/delete_category', methods=['GET'])
def delete_category():
	key = request.args.get('key', None)
	if key == '6666666':
		try:		
			query = db.session.query(distinct(func.substr(Goods.goods_category, 1, 3)))
			categories = query.all()
			cates = [str(d[0]) for d in categories]
			app.logger.debug(cates)
			db.session.execute('update tq_goods_category set category_level = 0 where category_level = 1')
			db.session.execute('update tq_goods_category set category_level = 1 where category_level = 0 and category_id in :ids', {'ids':cates})
			db.session.commit()

			return render_template('error.html', error_msg = cates)
		except Exception as e:
			db.session.rollback()
			print(e)
			traceback.print_exc()
	else:
		return render_template('error.html', error_msg = 'key error')

def get_category(category_name):
	cate_code = None
	# 用 / 分割
	categories = category_name.strip().split('/')
	level = len(categories) #总分类/当前分类级别
	leaf_cate = categories[level - 1].strip() #末级分类

	#查询该末级分类是否存在，如果存在，说明该分类的上级也存在
	cur_cate = GoodsCategory.query.filter_by(category_name = leaf_cate, category_level = level).first()
	# 分类不存在，需要插入该分类，以及其父类
	if cur_cate is None:
		# 把当前分类的插入
		# cate_code = add_category(leaf_cate, level, '')

		# 遍历添加所有分类
		parent_code = ''
		index = 1
		for cname in categories:
			_cate = GoodsCategory.query.filter_by(category_name = cname, category_level = index).first()
			if _cate is None:
				parent_code = add_category(cname, index, parent_code)
			else:
				parent_code = _cate.category_id

			index += 1

		cate_code = parent_code

	else:
		cate_code = cur_cate.category_id

	return cate_code


def add_category(name, level, parent_code):
	cate = GoodsCategory()

	# 获取category_id
	next_code = '000';
	#next_cate = GoodsCategory.query(func.max(GoodsCategory.category_id)).filter_by(category_level = level).first()
	#next_cate = db.session.select([func.max(GoodsCategory.category_id)]).where(GoodsCategory.category_level == level).execute().scalar()
	next_cate = db.session.query(func.max(GoodsCategory.category_id)).filter(GoodsCategory.category_level == level, GoodsCategory.category_id.like(parent_code + '%')).limit(1).scalar()
	if next_cate is not None:
		next_code = str(int(next_cate[-3:]) + 1).zfill(3)

	cate.category_id = parent_code + next_code
	cate.category_name = name
	cate.category_order = 0
	cate.category_level = level
	db.session.add(cate)
	db.session.commit()

	return cate.category_id

def sync_import(app, table, start_num):
	try:
		with app.app_context():				
				
			nrows = table.nrows #行数
			goods = None
			exec_count = 0
			for i in range(start_num, nrows):
				try:
					rowValues = table.row_values(i) #某一行数据
					goods_id = rowValues[0]
					# 判断该商品是否存在
					cur_goods = Goods.query.filter_by(goods_id = goods_id).first()
					if cur_goods is not None:
						db.session.delete(cur_goods)
						db.session.commit()
			
					goods = Goods()
					goods.goods_id = goods_id
					goods.goods_name = rowValues[1]
					goods.goods_img_url = rowValues[2]
					goods.goods_details_url = rowValues[3]
					
					# 获取分类编码
					#goods.goods_category = rowValues[4]
					goods.goods_category = get_category(rowValues[4]);
			
					goods.taobaoke_url = rowValues[5]
					goods.goods_price = float(rowValues[6])
					goods.goods_selled = rowValues[7]

					goods.income_ratio = float(rowValues[8])
					goods.commission = float(rowValues[9])

					goods.goods_shop_name = rowValues[12]
			
					#平台
					platform = rowValues[13].strip()
					if platform == '淘宝':
						platform = 'TAOBAO'
					elif platform == '天猫':
						platform = 'TIANMAO'
					goods.goods_platform = platform
			
					goods.goods_coupon = rowValues[17].strip() # 优惠券描述

					# 无优惠券
					if goods.goods_coupon is None or goods.goods_coupon == '无':
						goods.goods_coupon = '购买领返利'
						goods.goods_coupon_full_amt = 0
						goods.goods_coupon_amt = 0
						goods.goods_couponed_price = goods.goods_price


					else:
						# 获取满减券
						matchGroups = re.match(r'满([\d\.]+)[元]*减([\d\.]+)[元]*', goods.goods_coupon, re.M|re.I)
						if matchGroups is not None:
							groups = matchGroups.groups()
							goods.goods_coupon_full_amt = float(groups[0]) # 满减
							goods.goods_coupon_amt = float(groups[1]) # 优惠券金额
							# 如果满减金额大于商品金额，计算优惠后金额。否则，优惠金额为原价
							if goods.goods_price >= goods.goods_coupon_full_amt:
								goods.goods_couponed_price = goods.goods_price - goods.goods_coupon_amt
							else:
								goods.goods_couponed_price = goods.goods_price
				
							if goods.goods_couponed_price < 0:
								goods.goods_couponed_price = 0
						# 无条件券
						matchGroups = re.match(r'([\d\.]+)元无条件券', goods.goods_coupon, re.M|re.I)
						if matchGroups is not None:
							groups = matchGroups.groups()
							goods.goods_coupon_full_amt = 0
							goods.goods_coupon_amt = float(groups[0])
							goods.goods_couponed_price = goods.goods_price - goods.goods_coupon_amt
							
							if goods.goods_couponed_price < 0:
								goods.goods_couponed_price = 0


					goods.goods_coupon_total = rowValues[15]
					goods.goods_coupon_balance = rowValues[16]

					# 开始日期
					if rowValues[18] is None or len(rowValues[18].strip()) == 0:
						goods.googs_coupon_start_dt = '99999999'
					else:
						goods.googs_coupon_start_dt = str(rowValues[18]).replace('-', '')
					# 结束日期
					if rowValues[19] is None or len(rowValues[19].strip()) == 0:
						goods.googs_coupon_end_dt = '99999999'
					else:
						goods.googs_coupon_end_dt = str(rowValues[19]).replace('-', '')
					
					goods.googs_coupon_url = rowValues[20]
					goods.googs_coupon_buy_url = rowValues[21]
					goods.create_dt = time.strftime('%Y%m%d%H%M%S', time.localtime())
					goods.activity_id = rowValues[22]
			
					db.session.add(goods)
					db.session.commit()
					exec_count += 1

				except Exception as e:
					db.session.rollback()
					app.logger.error(e)
					continue
				
	except Exception as e:
		app.logger.error(e)
			
def sync_delete(app, datas):
	with app.app_context():
		for data in datas:
			cur_goods = Goods.query.filter_by(goods_id = data.goods_id).first()
			if cur_goods is not None:
				db.session.delete(cur_goods)
				db.session.commit()