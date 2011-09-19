# coding: utf-8

import datetime, hashlib

from sqlalchemy import sql, Column, String, Integer, Boolean, DateTime, Float, ForeignKey
from sqlalchemy.orm import relation, backref, column_property, synonym
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

from utils.coredb import BaseQuery, Base
from utils.escape import json_encode, json_decode

# TODO #2 redis cache the user's loud-id set  and when signup cache the pre-user's phone number

class UserQuery(BaseQuery):
    def get_by_phone(self, phn):
        ''' Get user from users table return the User object 
        or Not exisit and Multi exisit return None
        '''
         return self.filter_by(phone=phn, block=False).first()
    
    def get_by_token(self, token):
        ''' Get user from users table return the User object 
        or Not exisit and Multi exisit return None
        '''
        return self.filter_by(token=token, block=False).first()

class LoudQuery(BaseQuery):
    def get_by_cycle(self, user_lat, user_lon):
        return self.from_statement("SELECT * FROM louds WHERE \
                ABS(:earth_r*ACOS(SIN(:lat)*SIN(lat)*COS(:lon-lon)+COS(:lat)*COS(lat))*PI()/180) < \
                :distance limit :num").params(earth_r=6378137, lat=user_lat, lon=user_lon, \
                        distance=5000, num=100)

    def get_by_list(self):
        return self.filter_by(block=False).order_by('created desc').limit(1000)

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
        # non self get the (phone, name, avatar, last_longitude, last_atitude, updated)
        info = self.to_dict(exclude=['id', '_shadow', 'shadow', '_password', 'password', 'token', 'radius', 'is_admin', 'block', 'created', 'louds'])

        return info

    def user_to_dict_by_owner(self):
        # user get the (content longitude latitude grade created phone name avatar last_longitude last_atitude
        # loud_num is_admin distance updated created)
        info = self.to_dict(exclude=['id', '_password', 'password', 'token', 'block'])
        info['loud_num'] = self.loud_num
        info['louds'] = [e.to_dict(exclude=['id', 'user_id', 'block']) for e in self.louds]

        return info

    def user_to_dict_by_auth(self):
        info = self.to_dict(exclude=['id', '_shadow', 'shadow', '_password', 'password', 'radius',
            'is_admin', 'block', 'created', 'louds', 'avatar', 'last_lon', 'last_lat'])

        return info

class Loud(Base):
    __tablename__ = 'louds'

    query_class = LoudQuery

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    content = Column(String(70))
    lon = Column(Float, default=0)
    lat = Column(Float, default=0)
    address = Column(String(30), nullable=True)
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
        loud_dict = self.to_dict(exclude=['user_id', 'block'])
        loud_dict['user'] = self.user.to_dict(exclude=['id', '_password', 'password', 'token', 'radius','updated', 'is_admin', 'block', 'created', 'last_lon', 'last_lat'])

        return loud_dict

# user's all louds number
User.loud_num = column_property(sql.select([sql.func.count(Loud.id)]).\
        where(Loud.user_id==User.id).as_scalar(), deferred=True)
