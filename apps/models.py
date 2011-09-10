# coding: utf-8

import datetime, hashlib

from tornado.escape import json_encode, json_decode

from sqlalchemy import sql, Column, String, Integer, Boolean, DateTime, Float, ForeignKey
from sqlalchemy.orm import relation, backref, column_property, synonym
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

from utils.coredb import BaseQuery, Base

# TODO #2 redis cache the user's loud-id set  and when signup cache the pre-user's phone number

class UserQuery(BaseQuery):
    def get_by_phone(self, phn):
        ''' Get user from users table return the User object 
        or Not exisit and Multi exisit return None
        '''
        try:
            user = self.filter_by(phone=phn, block=False).one()
        except (NoResultFound, MultipleResultsFound):
            user = None
        return user
    
    def get_by_token(self, token):
        ''' Get user from users table return the User object 
        or Not exisit and Multi exisit return None
        '''
        try:
            user = self.filter_by(token=token, block=False).one()
        except (NoResultFound, MultipleResultsFound):
            user = None
        return user

class LoudQuery(BaseQuery):
    def get_by_cycle(self, u):
        # TODO #1 compute the loud cycle alr..
        return self.filter_by(block=False).order_by('created desc').limit(1000)

class User(Base):
    __tablename__ = 'users'

    query_class = UserQuery

    id = Column(Integer, primary_key=True)
    phone = Column(Integer, unique=True)
    _password = Column("password", String(32))
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

    def _get_password(self):
        return self._password
    
    def _set_password(self, password):
        self._password = hashlib.md5(password).hexdigest()
    
    password = synonym("_password", descriptor=property(_get_password, _set_password))

    def can_save(self):
        return self.phone and self.password and self.name 

    def owner_by(self, u):
        return u and u.id == self.id

    def user_to_dict(self, u):
        if self.owner_by(u):
            # owner 's 
            info = self.user_to_dict_by_owner()
        else:
            info = self.user_to_dict_by_other()

        return info

    def user_to_dict_by_other(self):
        # non self get the (phone, name, avatar, last_longitude, last_atitude, updated)
        info = self.to_dict(exclude=['id', '_password', 'password', 'token', 'radius', 'is_admin', 'block', 'created', 'louds'])

        return info

    def user_to_dict_by_owner(self):
        # user get the (content longitude latitude grade created phone name avatar last_longitude last_atitude
        # loud_num is_admin distance updated created)
        info = self.to_dict(exclude=['id', '_password', 'password', 'token', 'block'])
        info['loud_num'] = self.loud_num
        info['louds'] = [e.to_dict(exclude=['id', 'user_id', 'block']) for e in self.louds]

        return info


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

    def can_save(self):
        return self.user and self.content and self.lat and self.lon

    def owner_by(self, u):
        return u and u.id == self.user_id
    
    def loud_to_dict(self):
        loud_dict = self.to_dict(exclude=['id', 'user_id', 'block'])
        loud_dict['user'] = self.user.to_dict(exclude=['id', '_password', 'password', 'token', 'radius','updated', 'is_admin', 'block', 'created', 'last_lon', 'last_lat'])

        return loud_dict

# user's all louds number
User.loud_num = column_property(sql.select([sql.func.count(Loud.id)]).\
        where(Loud.user_id==User.id).as_scalar(), deferred=True)
