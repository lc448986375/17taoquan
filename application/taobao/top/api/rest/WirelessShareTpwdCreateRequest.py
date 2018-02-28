'''
Created by auto_sdk on 2017.10.12
'''
from application.taobao.top.api.base import RestApi
class WirelessShareTpwdCreateRequest(RestApi):
	def __init__(self,domain='gw.api.taobao.com',port=80):
		RestApi.__init__(self,domain, port)
		self.tpwd_param = None

	def getapiname(self):
		return 'taobao.wireless.share.tpwd.create'
