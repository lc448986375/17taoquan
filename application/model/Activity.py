#encoding=utf-8

from application import db

class Activity(db.Model):
    __tablename__ = 'tq_activity'

    id = db.Column(db.Integer, primary_key = True)
    activity_name = db.Column(db.String, unique = True)
    activity_status = db.Column(db.String, unique = True)

    def __init__(self):
        pass

    def __repr__(self):
        return '<Activity %r,%r>' % (self.id, self.activity_name)