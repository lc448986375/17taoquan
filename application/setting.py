# _*_ coding: utf-8 _*_

#调试模式是否开启
DEBUG = True

SQLALCHEMY_TRACK_MODIFICATIONS = True #如果使用全文搜搜，此处要改为True。全文搜索通过该属性出发提交时创建索引

#session必须要设置key
SECRET_KEY = 'A0ZkL8j/3yX R~XHH!jmN]LWX/,?RT'

SQLALCHEMY_ECHO = True

#mysql数据库连接信息,这里改为自己的账号
#SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:123456@localhost:3306/taoquan"
#SQLALCHEMY_DATABASE_URI = "mysql+pymysql://taoquan:tq+258046@66.112.215.5:3306/taoquan"
SQLALCHEMY_DATABASE_URI = "mysql://root:123456@localhost:3306/taoquan"

MSEARCH_INDEX_NAME = "application/data/whoosh/base"