# coding: utf-8

import datetime, hashlib, decimal

from sqlalchemy import sql, Column, String, Integer, Boolean, DateTime, Float, ForeignKey
from sqlalchemy.orm import relation, backref, column_property, synonym
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

from tornado.options import options

from utils.coredb import BaseQuery, Base
from utils.escape import json_encode, json_decode

# TODO #2 redis cache the user's loud-id set  and token

class UserQuery(BaseQuery):

    def get_users(self):
        return self.filter_by(block=False)

    def get_by_phone(self, phn):
        ''' Get user from users table return the User object 
        or Not exisit and Multi exisit return None
        '''
        # FIXME
        return self.get_users().filter_by(phone=phn).first()
    
    def get_by_token(self, token):
        ''' Get user from users table return the User object 
        or Not exisit and Multi exisit return None
        '''
        # FIXME
        return self.get_users().filter_by(token=token).first()


class LoudQuery(BaseQuery):

    def get_louds(self):
        return self.filter(Loud.block==False).filter(Loud.user_id>0)

    def get_by_cycle2(self, user_lat, user_lon):

        # geo args
        earth_r, distance = options.er, options.cr

        # ignore user's small movement lat: 55.66m, lon: 54.93m
        user_lat = decimal.Decimal(user_lat).quantize(decimal.Decimal('0.0001'))
        user_lon = decimal.Decimal(user_lon).quantize(decimal.Decimal('0.0001'))

        # mysql functions 
        acos, sin, cos, pi, abs = sql.func.acos, sql.func.sin, sql.func.cos, sql.func.pi, sql.func.abs

        return self.get_louds()\
                   .filter(abs(earth_r*acos(sin(user_lat)*sin(Loud.lat)*cos(user_lon-Loud.lon)+cos(user_lat)*cos(Loud.lat))*pi()/180)<distance)

    def get_by_cycle(self, user_lat, user_lon):
        return self.get_by_cycle2(user_lat, user_lon).limit(100)

    def get_by_cycle_key(self, user_lat, user_lon, key):
        return self.get_by_cycle2(user_lat, user_lon).filter(Loud.content.like('%'+key+'%'))


class User(Base):
    __tablename__ = 'users'

    query_class = UserQuery

    id = Column(Integer, primary_key=True)
    phone = Column(Integer, unique=True)
    _password = Column("password", String(32))
    name = Column(String(20))
    avatar = Column(String(100), nullable=True)
    token = Column(String(32), nullable=True)
    last_lat = Column(Float, default=0)
    last_lon = Column(Float, default=0)
    radius = Column(Float, nullable=True, default=2.5)
    _shadow = Column("shadow", String(2048), nullable=True)
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

    def _get_shadow(self):
        if self._shadow:
            return json_decode(self._shadow)

        return []

    def _set_shadow(self, data):
        self._shadow = json_encode(data)

    shadow = synonym("_shadow", descriptor=property(_get_shadow, _set_shadow))

    def can_save(self):
        return self.phone and self.password and self.name 

    def owner_by(self, u):
        return u and u.id == self.id

    def admin_by(self, u):
        return self.owner_by(u) or u.is_admin

    def authenticate(self, password):
        return self.password == hashlib.md5(password).hexdigest()

    def user_to_dict(self, u):
        if self.owner_by(u):
            # owner 's 
            info = self.user_to_dict_by_owner()
        else:
            info = self.user_to_dict_by_other()

        return info

    def user_to_dict_by_other(self):
        #  (id, link, phone, name, avatar, last_lon, last_lat, updated)
        info = self.to_dict(include=['phone', 'name', 'avatar', 'last_lat', 'last_lon', 'updated'])
        info['id'] = self.get_urn_id()
        info['link'] = self.get_link()
        info['avatar_link'] = self.get_avatar_link()

        return info

    def user_to_dict_by_owner(self):
        # (id, link, phone, name, avatar, last_lat, last_lon, is_admin, updated, created, radius,
        # loud_num)
        info = self.to_dict(include=['phone', 'name', 'avatar', 'last_lat', 'last_lon','is_admin',
            'radius', 'updated', 'created'])
        info['id'] = self.get_urn_id()
        info['link'] = self.get_link()
        info['avatar_link'] = self.get_avatar_link()
        info['loud_num'] = self.loud_num

        return info

    def user_to_dict_by_auth(self):
        info = self.to_dict(include=['name', 'token', 'phone', 'updated'])

        return info

    def get_link(self):
        return "%s%s" % (options.site_uri, self.reverse_uri('user', self.phone))

    def get_avatar_link(self):
        return "%s/%s" % (options.static_uri, self.avatar)


class Loud(Base):
    __tablename__ = 'louds'

    query_class = LoudQuery

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"))
    content = Column(String(70))
    lon = Column(Float, default=0)
    lat = Column(Float, default=0)
    address = Column(String(30), nullable=True)
    grade = Column(Integer, default=5)
    block = Column(Boolean, default=False)
    created = Column(DateTime, default=datetime.datetime.now)

    # on delete CASCADE make me a lots to fix it. 
    # use this feature you must do two things:
    # 1) Column ForeignKey set ondelete keyword for database level 
    # 2) mapper on relation set cascade keyword in parent Model for sqlalchemy session level 
    user = relation('User', backref=backref('louds', order_by=created,  cascade="all, delete, delete-orphan"))

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

    def admin_by(self, u):
        return self.owner_by(u) or u.is_admin
    
    def loud_to_dict(self):
        loud_dict = self.to_dict(include=['content', 'grade', 'address', 'lat', 'lon', 'created'])
        loud_dict['user'] = self.user.user_to_dict_by_other()
        
        loud_dict['id'] = self.get_urn_id()
        loud_dict['lid'] = self.id # FIXME let me out here
        loud_dict['link'] = self.get_link()

        return loud_dict

    def get_link(self):
        return "%s%s" % (options.site_uri, self.reverse_uri('loud', self.id))

# user's all louds number
User.loud_num = column_property(sql.select([sql.func.count(Loud.id)]).\
        where(Loud.user_id==User.id).as_scalar(), deferred=True)
