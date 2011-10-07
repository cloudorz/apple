# coding: utf-8

import hashlib

from tornado.web import HTTPError

from apps import BaseRequestHandler
from apps.models import User, Loud
from utils.decorator import authenticated, admin, owner
from utils.mkthings import QDict


class LoudHandler(BaseRequestHandler):

    @authenticated
    def get(self, lid):
        loud = Loud.query.get_by_key(lid)

        if loud:
            loud_dict = loud.loud_to_dict()
            self.render_json(loud_dict)
        else:
            self.set_status(404)
            self.render_json(self.message("the loud is not exsited"))

    @authenticated
    def post(self, lid):

        # the precondtion the max 3 louds.
        loud_count = Loud.query.get_louds().filter(Loud.user==self.current_user)).count()
        if loud_count > 3:
            raise HTTPError(412)

        data = self.get_data()

        loud = Loud()
        loud.user = self.current_user

        if self.current_user.is_admin:
            # admin's loud
            data['grade'] = 0

        loud.from_dict(data)

        if loud.save():
            self.set_status(201)
            self.set_header('Location', loud.get_link())
            msg = self.message("Created Success.")
        else:
            self.set_status(400)
            msg = self.message("content,lat,lon,address fields are required.")

        # addtional operation add the position
        self.current_user.last_lat = data['lat']
        self.current_user.last_lon = data['lon']
        self.current_user.save()

        self.render_json(msg)

    @authenticated
    @admin('lid', 'loud')
    def delete(self, loud):
        loud.block = True
        loud.save()

        self.render_json(self.message("Remove Succss."))

    def get_recipient(self, lid):
        return Loud.query.get_by_key(lid)


class SearchLoudhandler(BaseRequestHandler):

    @authenticated
    def get(self):
        condition = self.get_argument('q')
        if ':' in condition:
            field, value = condition.split(':')
        else:
            raise HTTPError(400)

        handle_q = {
                'author': lambda phn: Loud.query\
                        .get_louds()\
                        .filter(Loud.user.has(User.phone==phn)),
                'position': lambda data: Loud.query\
                        .get_by_cycle2(*data.split(',')),
                'key': lambda data: Loud.query\
                        .get_by_cycle_key(*data.split(',')),
                }

        if field in handle_q:
            q = QDict(
                    q=condition,
                    v=value,
                    sort=self.get_argument('qs'),
                    start=int(self.get_argument('st')),
                    num=int(self.get_argument('qn')),
                    )
            query_louds = handle_q[field](q.v)

            # composite the results collection
            total = query_louds.count()
            query_dict = {
                    'q': q.q,
                    'qs': q.sort,
                    'st': q.start,
                    'qn': q.num,
                    }

            loud_collection = {
                    'louds': [e.loud_to_dict() for e in query_louds.order_by(q.sort).limit(q.num).offset(q.start)],
                    'total': total,
                    'link': self.full_uri(query_dict),
                    }

            if q.start + q.num < total:
                query_dict['st'] = q.start + q.num
                loud_collection['next'] = self.full_uri(query_dict)

            if q.start > 0:
                query_dict['st'] = max(q.start - q.num, 0)
                loud_collection['prev'] = self.full_uri(query_dict)

            # make etag prepare
            self.cur_louds = loud_collection['louds']
        else:
            raise HTTPError(400)

        self.render_json(loud_collection)
    
    def compute_etag(self):

        hasher = hashlib.sha1()
        if 'cur_louds' in self.__dict__:
            any(hasher.update(e) for e in sorted(loud['id'] for loud in self.cur_louds))

        return '"%s"' % hasher.hexdigest()

