#encoding=utf-8

from application import app, db
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, SignatureExpired, BadSignature
from passlib.apps import custom_app_context as pwd_context
from marshmallow import Schema, fields

class User(db.Model):
    __tablename__ = 'tq_user'

    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.String, unique = True)
    user_nickname = db.Column(db.String, unique = True)
    user_password = db.Column(db.String, unique = True)
    user_wx = db.Column(db.String, unique = True)
    user_wx_id = db.Column(db.String, unique = True)
    status = db.Column(db.String, unique = True)
    email = db.Column(db.String, unique = True)
    wallet_amt = db.Column(db.Numeric)

    def __init__(self):
        pass

    # 生成token
    # 超时时间 60 * 60 * 24 * 30 一个月
    def generate_auth_token(self, expiration = 2592000):
        s = Serializer(app.config['SECRET_KEY'], expires_in = expiration)
        return s.dumps({'user_id': self.user_id}).decode()

    # 密码加密
    def hash_password(self, password):
        self.user_password = pwd_context.encrypt(password)

    # 校验密码
    def verify_password(self, password):
        app.logger.debug(self.user_password)
        return pwd_context.verify(password, self.user_password)

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None # token 到期
        except BadSignature:
            return None # token 错误

        # 校验成功，根据ID返回用户
        user = User.query.filter_by(user_id = data['user_id']).first()
        return user


    def __repr__(self):
        return '<User %r, %r>' % (self.id, self.user_id)


class UserSchema(Schema):
    id = fields.Int()
    user_id = fields.Str()
    user_nickname = fields.Str()
    # user_password = fields.Str()
    # user_wx = fields.Str()
    # user_wx_id = fields.Str()
    # status = fields.Str()
    email = fields.Str()
    wallet_amt = fields.Number()

class UserDao():
    def add(self, user_obj):
        user = User()
        user.user_id = user_obj['username']
        user.user_nickname = user_obj['nickname']
        user.hash_password(user_obj['password']) # 生成密码
        user.status = 'Y'
        user.wallet_amt = 0

        db.session.add(user)
        db.session.commit()