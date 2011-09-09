# coding: utf-8

import datetime

from tornado.escape import json_encode, json_decode

from sqlalchemy import sql, Column, String, Integer, Boolean, DateTime, Float, ForeignKey
from sqlalchemy.orm import relation, backref, column_property
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

from utils.coredb import BaseQuery, Base

class UserQuery(BaseQuery):
    def get_by_phone(self, phn):
        ''' Get user from users table return the User object 
        or Not exisit and Multi exisit return None
        '''
        try:
            user = self.filter_by(phone=phn).one()
        except (NoResultFound, MultipleResultsFound):
            user = None
        return user
    
    def get_by_token(self, token):
        ''' Get user from users table return the User object 
        or Not exisit and Multi exisit return None
        '''
        try:
            user = self.filter_by(token=token).one()
        except (NoResultFound, MultipleResultsFound):
            user = None
        return user

class LoudQuery(BaseQuery):
    pass

class User(Base):
    __tablename__ = 'users'

    query_class = UserQuery

    id = Column(Integer, primary_key=True)
    phone = Column(Integer, unique=True)
    password = Column(String(32))
    name = Column(String(20))
    avatar = Column(String(100), nullable=True)
    token = Column(String(64), nullable=True)
    last_lon = Column(Float, default=0)
    last_lat = Column(Float, default=0)
    radius = Column(Float, nullable=True, default=2.5)
    is_admin = Column(Boolean, default=False)
    block = Column(Boolean, default=False)
    updated = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    created = Column(DateTime, default=datetime.datetime.now)

    def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)

    def __repr__(self):
        return "<user:%s>" % self.phone

    def __str__(self):
        return "<user:%s>" % self.phone


class Loud(Base):
    __tablename__ = 'louds'

    query_class = LoudQuery

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    content = Column(String(70))
    lon = Column(Float, default=0)
    lat = Column(Float, default=0)
    grade = Column(Integer, default=5)
    block = Column(Boolean, default=False)
    created = Column(DateTime, default=datetime.datetime.now)

    user = relation('User', backref=backref('louds', order_by=created))

    def __init__(self, *args, **kwargs):
        super(Loud, self).__init__(*args, **kwargs)

    def __repr__(self):
        return "<loud:%s>" % self.id

    def __str__(self):
        return "<loud:%s>" % self.id


# user's all louds number
User.loud_num = column_property(sql.select([sql.func.count(Loud.id)]).\
        where(Loud.user_id==User.id).as_scalar(), deferred=True)
