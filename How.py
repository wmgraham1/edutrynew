import jinja2
import os
import webapp2
import logging
from datetime import datetime
from google.appengine.ext import db
from google.appengine.ext import ndb
from google.appengine.api import users
from webapp2_extras import sessions
from google.appengine.api import memcache
from SecurityUtils import AccessOK

from models import Papers


TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'templates')
jinja_environment = \
    jinja2.Environment(loader=jinja2.FileSystemLoader(TEMPLATE_DIR))
jinja_environment.filters['AccessOK'] = AccessOK

#jinja_environment = jinja2.Environment(autoescape=True,
#    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')))

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

    def dispatch(self):
        # Get a session store for this request.
        self.session_store = sessions.get_store(request=self.request)

        try:
            # Dispatch the request.
            webapp2.RequestHandler.dispatch(self)
        finally:
            # Save all sessions.
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def session(self):
        # Returns a session using the default cookie key.
        return self.session_store.get_session()

class HowIntro(BaseHandler):
    def get(self):

        logout = None
        login = None
        currentuser = users.get_current_user()
        if currentuser:
              logout = users.create_logout_url('/' )
        else:
              login = users.create_login_url('/')

        template_values = {'currentuser':currentuser, 'login':login, 'logout': logout}

        template = jinja_environment.get_template('HowIntro.html')
        jinja_environment.filters['AccessOK'] = AccessOK

        self.response.out.write(template.render(template_values))

class HowTrans(BaseHandler):
    def get(self):

        logout = None
        login = None
        currentuser = users.get_current_user()
        if currentuser:
              logout = users.create_logout_url('/' )
        else:
              login = users.create_login_url('/')

        template_values = {'currentuser':currentuser, 'login':login, 'logout': logout}

        template = jinja_environment.get_template('HowTrans.html')
        jinja_environment.filters['AccessOK'] = AccessOK

        self.response.out.write(template.render(template_values))

class HowTransTheory(BaseHandler):
    def get(self):

        logout = None
        login = None
        currentuser = users.get_current_user()
        if currentuser:
              logout = users.create_logout_url('/' )
        else:
              login = users.create_login_url('/')

        template_values = {'currentuser':currentuser, 'login':login, 'logout': logout}

        template = jinja_environment.get_template('HowTransTheory.html')
        jinja_environment.filters['AccessOK'] = AccessOK

        self.response.out.write(template.render(template_values))
