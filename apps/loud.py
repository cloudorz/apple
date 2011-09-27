# coding: utf-8

from apps import BaseRequestHandler
from apps.models import User, Loud
from utils.decorator import authenticated, admin, owner
from utils.constants import Fail, Success

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
        data = self.get_data()

        loud = Loud()
        loud.user = self.current_user

        if self.current_user.is_admin:
            # admin's loud
            data['grade'] = 0

        loud.from_dict(data)

        if loud.save():
            self.set_status(201)
            self.set_header('Location', "http://%s%s" % (self.request.host, self.reverse_url('loud', loud.id)))
            msg = self.message("Created Success.")
        else:
            self.set_status(400)
            msg = self.message("content,lat,lon fields are required.")

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


class LoudSearchHandler(BaseRequestHandler):

    @authenticated
    def get(self):
        
        louds = Loud.query.get_by_cycle(self.get_argument('lat'), self.get_argument('lon'))

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


class LoudManageHandler(BaseRequestHandler):

    @authenticated
    def get(self):
        louds = Loud.query.filter(Loud.user==self.current_user).filter(Loud.block==False).filter(Loud.id>0).limit(3)
        res = [{'pk':e.id, 'content': e.content} for e in louds]

        self.render_json(res)
