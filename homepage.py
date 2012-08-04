import jinja2
import os
import webapp2
import logging
from datetime import datetime
from google.appengine.ext import db
from webapp2_extras import sessions
from google.appengine.api import memcache

from models import PageContents

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'templates')
jinja_environment = \
    jinja2.Environment(loader=jinja2.FileSystemLoader(TEMPLATE_DIR))

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

class ViewHomePage(BaseHandler):
    def get(self):
        PageContentList = memcache.get("PageContentList")
        if PageContentList is not None:
            logging.info("got PageContentList from memcache.")
        else:
            logging.info("Can not get PageContentList from memcache.")
            PageContent = PageContents.all()
            PageContentList = {}
            for PageCntnt in PageContent:
                PageContentList[PageCntnt.TemplateName] = PageCntnt.key().id()
            if not memcache.add("PageContentList", PageContentList, 10):
                logging.info("Memcache set failed.")
            else:
                logging.info("Memcache set succeeded.")

        if PageContentList.has_key('homepage'):
            template_id = (PageContentList['homepage'])
            iden = int(template_id)
            PageContent = db.get(db.Key.from_path('PageContents', iden))
            template_values = {
                'content1': PageContent.ContentText}
        else:
            template_values = {
                'content1': 'No home page content yet.'}
        template = jinja_environment.get_template('stdpage_block.html')
        self.response.out.write(template.render(template_values))
