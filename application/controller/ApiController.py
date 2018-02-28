#encoding=utf-8

from application import app, db, resp_200, resp_403, resp_404, resp_500
from flask import jsonify, make_response, g, request
from flask_httpauth import HTTPBasicAuth
from application.model.User import User, UserSchema, UserDao
from application.model.UserOrders import UserOrdersDao, UserOrdersSchema
from application.model.Goods import GoodsSchema, GoodsDao
from application.model.GoodsClass import GoodsClass, GoodsClassSchema, GoodsClassDao
from application.model.Wallet import WalletDao
from application.model.GoodsOrder import GoodsOrderDao

auth = HTTPBasicAuth()

######################################################################
### 用户接口
######################################################################
## 用户创建
@app.route('/api/v1.0/user/regist', methods=['POST'])
def regist():
    username = request.form.get('username', '')
    nickname = request.form.get('nickname', '')
    password = request.form.get('password', '')
    re_password = request.form.get('re_password', '')

    if password != re_password:
        return resp_500('两次密码不一致')

    user = User.query.filter_by(user_id = username).first()
    if user:
        return resp_500('用户名:' + username + '已存在')

    userDao = UserDao()
    user = {
        'username':username,
        'nickname':nickname,
        'password':password
    }
    userDao.add(user)

    return resp_200('新增成功')

## 获取用户信息
@app.route('/api/v1.0/user', methods=['GET'])
@auth.login_required
def userinfo():
    schema = UserSchema()
    result = schema.dump(g.user)
    return resp_200(result.data)



######################################################################
### 用户认证接口
######################################################################
'''
根据用户名、密码生成token
'''
@app.route('/api/v1.0/token', methods=['GET'])
@auth.login_required
def token():
    token = g.user.generate_auth_token()
    return resp_200(token)


@auth.verify_password
def verify_password(userid_or_token, password):
    # 首先校验，传入的是否为token，如果不是，则校验是否为用户、密码
    user = User.verify_auth_token(userid_or_token)
    if not user:
        user = User.query.filter_by(user_id = userid_or_token).first()
        if not user or not user.verify_password(password):
            return False
    
    g.user = user

    return True


# 认证失败
@auth.error_handler
def unauthorized():
    # return make_response(jsonify({'error': 'Unauthorized access'}), 401) 401 在客户端会弹出登录验证窗口
    return resp_403('认证失败')


######################################################################
### 订单接口
######################################################################
# 用户订单新增
# 传入商城订单ID
@app.route('/api/v1.0/userorders/<mall_order_id>', methods=['POST'])
@auth.login_required
def add_user_orders(mall_order_id):
    userOrderDao = UserOrdersDao()
    userOrderDao.add(g.user.id, mall_order_id)
    return resp_200('关联成功')

# 获取用户订单
@app.route('/api/v1.0/userorders', methods=['GET'])
@auth.login_required
def get_user_orders():
    userOrderDao = UserOrdersDao()
    userOrdersSchema = UserOrdersSchema()
    orders = userOrdersSchema.dump(userOrderDao.get_orders_by_user(g.user.id), many = True).data

    return resp_200(orders)


######################################################################
### 钱包接口
######################################################################
# 获取钱包金额
@app.route('/api/v1.0/wallet', methods=['GET'])
@auth.login_required
def get_wallet_info():
    res = {}
    walletDao = WalletDao()
    res['cf_amt'] = walletDao.get_cf_amt(g.user.id)

    return resp_200(res)


######################################################################
### 商品接口
######################################################################
@app.route('/api/v1.0/goods', methods=['GET'])
def goods_get():
    f = request.args.get('f', 'search')
    goodsDao = GoodsDao()
    schema = GoodsSchema()
    res = {}
    
    key_words = request.args.get('kwd', '')
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 30))

    args = {}        
    args['cate'] = str(request.args.get('cate', ''))
    args['order'] = request.args.get('order', '')
    args['activity'] = int(request.args.get('activity', 0))
    args['classes'] = request.args.get('cls', '')

    if len(args['cate']) == 2:
        args['classes'] = args['cate']

    pagination = goodsDao.search(key_words, page, page_size, **args)
    res['items'] = schema.dump(pagination.items, many = True).data

    res['page'] = {
        'pages' : pagination.pages,
        'page' : pagination.page,
        'has_next' : pagination.has_next
    }

    return resp_200(res)

# 显示商品明细
@app.route('/api/v1.0/goods/<id>', methods=['GET'])
def goods_details(id):
    goodsDao = GoodsDao()
    schema = GoodsSchema()
    res = {}
    goods = goodsDao.get_by_id(id)
    if goods is not None:
        res = schema.dump(goods).data
    else:
        res = {}

    return resp_200(res)

# 根据产品获取淘口令
@app.route('/api/v1.0/taokouling/<id>', methods=['GET'])
def goods_taokouling(id):
    goodsDao = GoodsDao()
    
    goods = goodsDao.get_by_id(id)
    tkl = goodsDao.get_tkl_by_url(goods.googs_coupon_buy_url)
    if tkl is None:
        return resp_500('淘口令生成失败, 请稍候再试')
    
    tkl = "[" + goods.goods_name + "]\n复制这条信息, " + tkl + ", 打开手机淘宝, 即可在手机淘宝中领券购买. 来自[一起淘券网(17taoquan.wang)]优惠分享"

    return resp_200(tkl)

# 大分类
@app.route('/api/v1.0/goodsclass', methods=['GET'])
def goods_class_get():
    classSchema = GoodsClassSchema()
    goodsClassDao = GoodsClassDao()
    res = classSchema.dump(goodsClassDao.get_cls(), many = True).data

    return resp_200(res)

# 排序
@app.route('/api/v1.0/goodsorder', methods=['GET'])
def goods_order_get():
    goodsOrderDao = GoodsOrderDao()
    res = goodsOrderDao.get_order()
    return resp_200(res)
