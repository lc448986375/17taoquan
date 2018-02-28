from flask import Flask, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_msearch import Search
from jieba.analyse import ChineseAnalyzer

#创建项目对象
app = Flask(__name__)

#加载配置文件内容
app.config.from_object('application.setting') #模块下的setting文件名，不用加py后缀 


#创建数据库对象 
db = SQLAlchemy(app)

# 全文搜索
full_search = Search(analyzer = ChineseAnalyzer())
full_search.init_app(app)

def resp_200(data):
    return jsonify(data)

def resp_500(error_msg):
    return make_response(jsonify({'error': error_msg}), 500)

def resp_403(error_msg):
    return make_response(jsonify({'error': error_msg}), 403)

def resp_404(error_msg):
    return make_response(jsonify({'error': error_msg}), 404)

from application.controller import SearchController, ImportController, DetailController, WeiXinController, MobileController, UserController, ApiController