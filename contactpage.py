import jinja2
import os
import webapp2
from datetime import datetime
from google.appengine.ext import db
from webapp2_extras import sessions
from Security import AccessOK

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'templates')
jinja_environment = \
    jinja2.Environment(loader=jinja2.FileSystemLoader(TEMPLATE_DIR))
jinja_environment.filters['AccessOK'] = AccessOK

#jinja_environment = jinja2.Environment(autoescape=True,
#    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')))
html = 'This is the more new contact us content.'

class BaseHandler(webapp2.RequestHandler):
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

class ViewContactPage(BaseHandler):
    def get(self):
        foo = self.session.get('langCode')

        html = 'This is the contact page.  The current language is '

        template_values = {
            'content1': html + foo
        }
        template = jinja_environment.get_template('stdpage_block.html')
        self.response.out.write(template.render(template_values))
