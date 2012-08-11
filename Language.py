import jinja2
import os
import webapp2
from datetime import datetime
from google.appengine.ext import db
from google.appengine.ext import ndb
from google.appengine.api import users

from models import Languages

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'templates')
jinja_environment = \
    jinja2.Environment(loader=jinja2.FileSystemLoader(TEMPLATE_DIR))


class LangBaseHandler(webapp2.RequestHandler):

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


class LangList(LangBaseHandler):

    def get(self):
        languages = Languages.query()
        logout = None
        login = None
        currentuser = users.get_current_user()
        if currentuser:
              logout = users.create_logout_url('/langs' )
        else:
              login = users.create_login_url('/langs/create')
        self.render_template('LangList.html', {'languages': languages,'currentuser':currentuser, 'login':login, 'logout': logout})

class LangCreate(LangBaseHandler):
    def post(self):
        n = Languages(langName=self.request.get('langName'),
                  langCode=self.request.get('langCode'),
                  langCode3=self.request.get('langCode3')
                  )
        n.put()
        return webapp2.redirect('/langs')

    def get(self):
        logout = None
        login = None
        currentuser = users.get_current_user()
        if currentuser:
              logout = users.create_logout_url('/langs' )
        else:
              login = users.create_login_url('/langs/create')
        self.render_template('LangCreate.html', {'currentuser':currentuser, 'login':login, 'logout': logout})

class LangEdit(LangBaseHandler):

    def post(self, lang_id):
        iden = int(lang_id)
        lang = ndb.Key('Languages', iden).get()
#        lang = db.get(db.Key.from_path('Languages', iden))
        currentuser = users.get_current_user()

        lang.langName = self.request.get('langName')
        lang.langCode = self.request.get('langCode')
        lang.langCode3 = self.request.get('langCode3')
        lang.put()
        return webapp2.redirect('/langs')

    def get(self, lang_id):
        iden = int(lang_id)
#        lang = db.get(db.Key.from_path('Languages', iden))
        lang = ndb.Key('Languages', iden).get()
        currentuser = users.get_current_user()

        logout = None
        login = None
        currentuser = users.get_current_user()
        if currentuser:
              logout = users.create_logout_url('/langs' )
        else:
              login = users.create_login_url('/langs')
        self.render_template('LangEdit.html', {'lang': lang,'currentuser':currentuser, 'login':login, 'logout': logout})


class LangDelete(LangBaseHandler):

    def get(self, lang_id):
        iden = int(lang_id)
#        lang = db.get(db.Key.from_path('Languages', iden))
        lang = ndb.Key('Languages', iden).get()
        currentuser = users.get_current_user()
        lang.key.delete()
#        db.delete(lang)
        return webapp2.redirect('/langs')
