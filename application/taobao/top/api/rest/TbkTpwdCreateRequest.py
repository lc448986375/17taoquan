'''
Created by auto_sdk on 2017.08.23
'''
from application.taobao.top.api.base import RestApi
class TbkTpwdCreateRequest(RestApi):
	__domain = None, 
	__port = None,
	
	def __init__(self,domain='gw.api.taobao.com',port=80):
		RestApi.__init__(self,domain, port)
		self.__domain = domain
		self.__port = port
		self.ext = None
		self.logo = None
		self.text = None
		self.url = None
		self.user_id = None

	def getapiname(self):
		return 'taobao.tbk.tpwd.create'
