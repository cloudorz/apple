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
    pass

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
