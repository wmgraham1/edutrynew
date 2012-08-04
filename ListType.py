import jinja2
import os
import webapp2
from datetime import datetime
from google.appengine.ext import db
from google.appengine.api import users

from models import ListTypes

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'templates')
jinja_environment = \
    jinja2.Environment(loader=jinja2.FileSystemLoader(TEMPLATE_DIR))


class BaseHandler(webapp2.RequestHandler):

    @webapp2.cached_property
    def jinja2(self):
        return jinja2.get_jinja2(app=self.app)

    def render_template(
        self,
        filename,
        template_values,
        **template_args
        ):
        template = jinja_environment.get_template(filename)
        self.response.out.write(template.render(template_values))


class ListTypeList(BaseHandler):

    def get(self):
        listtypes = ListTypes.all()
        logout = None
        login = None
        currentuser = users.get_current_user()
        if currentuser:
              logout = users.create_logout_url('/listtypes' )
        else:
              login = users.create_login_url('/listtypes/create')
        self.render_template('ListTypeList.html', {'listtypes': listtypes,'currentuser':currentuser, 'login':login, 'logout': logout})

class ListTypeCreate(BaseHandler):
    def post(self):
        n = ListTypes(ListTypeName=self.request.get('ListTypeName'),
                  ListTypeCode=self.request.get('ListTypeCode'),
                  Description=self.request.get('Description')
                  )
        n.put()
        return webapp2.redirect('/listtypes')

    def get(self):
        logout = None
        login = None
        currentuser = users.get_current_user()
        if currentuser:
              logout = users.create_logout_url('/listtypes' )
        else:
              login = users.create_login_url('/listtypes/create')
        self.render_template('ListTypeCreate.html', {'currentuser':currentuser, 'login':login, 'logout': logout})

class ListTypeEdit(BaseHandler):

    def post(self, listtype_id):
        iden = int(listtype_id)
        listtypes = db.get(db.Key.from_path('ListTypes', iden))
        currentuser = users.get_current_user()

        listtypes.ListTypeName = self.request.get('ListTypeName')
        listtypes.ListTypeCode = self.request.get('ListTypeCode')
        listtypes.Description = self.request.get('Description')
        listtypes.put()
        return webapp2.redirect('/listtypes')

    def get(self, lang_id):
        iden = int(lang_id)
        listtypes = db.get(db.Key.from_path('ListTypes', iden))
        currentuser = users.get_current_user()

        logout = None
        login = None
        currentuser = users.get_current_user()
        if currentuser:
              logout = users.create_logout_url('/listtypes' )
        else:
              login = users.create_login_url('/listtypes')
        self.render_template('LangEdit.html', {'listtypes': listtypes,'currentuser':currentuser, 'login':login, 'logout': logout})


class ListTypeDelete(BaseHandler):

    def get(self, lang_id):
        iden = int(lang_id)
        listtypes = db.get(db.Key.from_path('ListTypes', iden))
        currentuser = users.get_current_user()

        db.delete(listtypes)
        return webapp2.redirect('/listtypes')
