'''
Created by auto_sdk on 2017.06.21
'''
from application.taobao.top.api.base import RestApi
class TbkDgItemCouponGetRequest(RestApi):
	def __init__(self,domain='gw.api.taobao.com',port=80):
		RestApi.__init__(self,domain, port)
		self.adzone_id = None
		self.cat = None
		self.page_no = None
		self.page_size = None
		self.platform = None
		self.q = None

	def getapiname(self):
		return 'taobao.tbk.dg.item.coupon.get'
