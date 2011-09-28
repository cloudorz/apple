# coding: utf-8

from tornado.web import HTTPError
from tornado.httputil import url_concat
from tornado.options import options

from apps import BaseRequestHandler
from apps.models import User, Loud
from utils.decorator import authenticated, admin, owner
from utils.constants import Fail, Success


class LoudHandler(BaseRequestHandler):

    @authenticated
    def get(self, lid):
        if lid:
            loud = Loud.query.get_by_key(lid)

            if loud:
                loud_dict = loud.loud_to_dict()
                self.render_json(loud_dict)
            else:
                self.set_status(404)
                self.render_json(self.message("the loud is not exsited"))
        else:
            louds = Loud.query.get_by_cycle(self.get_argument('lat'), self.get_argument('lon'))
            
            # FIXME
            loud_dicts = [e.loud_to_dict() for e in louds]
            self.render_json({'add': loud_dicts, 'del': []})
            return

            shadow_loud_set = set(self.current_user.shadow)
            query_loud_set = set(e.id for e in louds)

            loud_add_set = query_loud_set - shadow_loud_set
            loud_del_set = shadow_loud_set - query_loud_set

            # save the new shadow
            self.current_user.shadow = list(query_loud_set)
            self.current_user.save()

            # the new loud
            loud_dicts = [e.loud_to_dict() for e in louds if e.id in loud_add_set]

            self.render_json({'add': loud_dicts, 'del': list(loud_del_set)})

    @authenticated
    def post(self, lid):
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


class LoudManageHandler(BaseRequestHandler):

    @authenticated
    def get(self):
        louds = Loud.query.filter(Loud.user==self.current_user).filter(Loud.block==False).filter(Loud.id>0).limit(3)
        res = [{'pk':e.id, 'content': e.content} for e in louds]

        self.render_json(res)


class SearchLoudhandler(BaseRequestHandler):

    def get(self):
        condition = self.get_argument('filter')
        if ':' in condition:
            field, data = condition.split(':')
        else:
            raise HTTPError(400)

        handle_q = {
                'author': self.q_author,
                'position': self.q_position,
                'key': self.q_key,
                }

        if field in handle_q:
            loud_dict = handle_q[field](data)
        else:
            raise HTTPError(400)

        self.render_json(loud_dict)

    def q_author(self, data):
        phn = data
        sort_str = self.get_argument('sortBy')
        st = int(self.get_argument('start'))
        limit = int(self.get_argument('offset'))

        user = User.query.get_by_phone(phn)
        louds = Loud.query.filter(Loud.user==user).\
                           filter(Loud.block==False).\
                           filter(Loud.id>0).\
                           order_by(sort_str)
        total = louds.count()
        res = {
                'louds': [e.loud_to_dict() for e in louds.limit(limit).offset(st)],
                'total': total,
                'link': self.request.full_url(),
                }

        # TODO compute the  prev or next 
        query_dict = {
                'filter': self.get_argument('filter'),
                'sortBy': sort_str,
                'start': st,
                'offset': limit,
                }

        if st + limit < total:
            query_dict['start'] = st + limit
            res['next'] = url_concat("%s%s" % (options.site_uri, self.request.path), query_dict)

        if st > 0:
            query_dict['start'] = max(st - limit, 0)
            res['prev'] = url_concat("%s%s" % (options.site_uri, self.request.path), query_dict)

        return res

    def q_position(self, data):
        lat, lon = data.split(',')
        sort_str = self.get_argument('sortBy')
        st = int(self.get_argument('start'))
        limit = int(self.get_argument('offset'))

        louds = Loud.query.get_by_cycle2(lat, lon, st, limit, sort_str)

        res = {
                'louds': [e.loud_to_dict() for e in louds],
                'total': louds.count(),
                'link': self.request.full_url(),
                }

        # TODO compute the  prev or next 

        return res

    def q_key(self, data):
        lat,lon,q = data.split(',')

        sort_str = self.get_argument('sortBy')
        st = int(self.get_argument('start'))
        limit = int(self.get_argument('offset'))

        louds = Loud.query.filter(Loud.content.like('%'+q+'%')).get_by_cycle2(lat, lon, st, limit, sort_str)

        res = {
                'louds': [e.loud_to_dict() for e in louds],
                'total': louds.count(),
                'link': self.request.full_url(),
                }

        # TODO compute the  prev or next 

        return res

