# coding: utf-8

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import class_mapper, Query
from sqlalchemy.orm.exc import UnmappedClassError, NoResultFound, MultipleResultsFound

class SQLAlchemy(object):
    ''' Get the sqlalchemy session
    '''
    def __init__(self):
        self.db_session = None
    
    def init_app(self, app=None):
        if app:
            self.db_session = app.db_session

sql_db = SQLAlchemy()

class BaseQuery(Query):
    ''' common custom query
    '''
    def get_by_key(self, tid):
        try:
            obj = self.filter_by(id=tid, block=False).one()
        except (NoResultFound, MultipleResultsFound):
            obj = None
        return obj


class _QueryProperty(object):
    ''' User.query.
    '''
    def __get__(self, obj, obj_cls):
        try:
            mapper = class_mapper(obj_cls)
            if mapper:
                return obj_cls.query_class(mapper, session=sql_db.db_session)
        except UnmappedClassError:
            return None

# this way create class vars is ok, the subclass also can inherit it
Base = declarative_base()
Base.db = sql_db.db_session
Base.query_class = BaseQuery
Base.query = _QueryProperty()

def obj_to_dict(self, exclude=[]):
    ''' convent the object to the dcit type
    not contain the relating objects
    '''
    exclude.append('_sa_instance_state')
    dict_obj = vars(self).copy()
    [dict_obj.pop(e) for e in dict_obj.keys() if e in exclude]
       
    return dict_obj

def obj_from_dict(self, data):
    # PS: not contain the user and not method name
    attrs = [e for e in dir(self) if not e.startswith('_') and not callable(getattr(self, e))]
    [setattr(self, e, data[e]) for e in data.keys() if e in attrs]

def obj_save(self):
    if self.can_save():
        print Base.db
        print sql_db.db_session
        self.db.commit()
        return True
        

Base.to_dict = obj_to_dict
Base.from_dict = obj_from_dict
Base.save = obj_save
