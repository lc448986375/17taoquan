#encoding=utf-8

import hashlib
from flask import request
from application import app
import xml.etree.ElementTree as ET
import time
from application.model.Goods import Goods, GoodsSchema
import traceback

@app.route('/wechat', methods=['GET','POST'])
def wechat():
	try:
		# 处理消息
		if request.method == 'POST':
			rec = xml_map(request.data)

			res_content = search_key(rec['content'])
			content = '没有找到[%s]的优惠' % rec['content']
			if res_content is not None and len(res_content) > 0:
				content = res_content + "\n点击链接领券购买, 如果访问被阻止,点击[继续访问]即可"

			resp = (rec['fromUser'], rec['toUser'], str(time.time() * 1000), content)
			return msg_template('text', resp)

		# 校验
		elif request.method == 'GET':
			return valid_msg(request)

	except Exception as e:
		app.logger.error(e)
		traceback.print_exc()

def valid_msg(request):
	
	token = '17taoquan'
	data = request.args
	signature = data.get('signature','')
	timestamp = data.get('timestamp','')
	nonce = data.get('nonce','')
	echostr = data.get('echostr','')
	list = [token, timestamp, nonce]
	list.sort()
	s = list[0] + list[1] + list[2]
	hascode = hashlib.sha1(s.encode('utf-8')).hexdigest()
	if hascode == signature:
		return echostr
	else:
		return None

def xml_map(str_xml):
	data = {}
	xml = ET.fromstring(str_xml)
	data['msgType'] = xml.find('MsgType').text
	data['fromUser'] = xml.find('FromUserName').text
	data['toUser'] = xml.find('ToUserName').text
	data['content'] = xml.find('Content').text

	return data


def msg_template(msgType, msg):
	
	textTpl = '''
		<xml>
			<ToUserName><![CDATA[%s]]></ToUserName>
			<FromUserName><![CDATA[%s]]></FromUserName>
			<CreateTime>%s</CreateTime>
			<MsgType><![CDATA[text]]></MsgType>
			<Content><![CDATA[%s]]></Content>
			<FuncFlag>0</FuncFlag>
		</xml>
	'''

	pictextTpl = '''
		<xml>
			<ToUserName><![CDATA[%s]]></ToUserName>
			<FromUserName><![CDATA[%s]]></FromUserName>
			<CreateTime>%s</CreateTime>
			<MsgType><![CDATA[news]]></MsgType>
			<ArticleCount>1</ArticleCount>
			<Articles>
			<item>
				<Title><![CDATA[%s]]></Title>
				<Description><![CDATA[%s]]></Description>
				<PicUrl><![CDATA[%s]]></PicUrl>
				<Url><![CDATA[%s]]></Url>
			</item>
			</Articles>
			<FuncFlag>1</FuncFlag>
		</xml>
	'''

	if msgType == 'text':
		return textTpl % msg
	else:
		return pictextTpl % msg

def search_key(key_words):
	content = '';

	query_temp = None
	query_temp = Goods.query.msearch(key_words, fields = ['goods_name'])
	query_temp = query_temp.order_by(Goods.income_ratio.desc())
	goods = query_temp.first()
	if goods is not None:
		content = content + goods2content(goods) + "\n\n"

	query_temp = None
	query_temp = Goods.query.msearch(key_words, fields = ['goods_name'])
	query_temp = query_temp.order_by(Goods.goods_couponed_price.asc())
	goods = query_temp.first()
	if goods is not None:
		content = content + goods2content(goods) + "\n\n"

	query_temp = None
	query_temp = Goods.query.msearch(key_words, fields = ['goods_name'])
	query_temp = query_temp.order_by(Goods.goods_selled.desc())
	goods = query_temp.first()
	if goods is not None:
		content = content + goods2content(goods)

	return content


def goods2content(goods):
	goods_obj = goods_to_dict(goods)
	content = '''
		%s\n
		原价:%s\n
		优惠券:%s\n
		返利:%s\n
		到手价:%s\n
		链接:%s
	''' % (goods_obj['goods_name'], goods_obj['goods_price'], goods_obj['goods_coupon'], 
				goods_obj['fanli_amt'], goods_obj['rebated_price'], 'https://17taoquan.wang/show/' + str(goods_obj['id']))

	return content