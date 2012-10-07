import jinja2
import os
import webapp2
from datetime import datetime
from google.appengine.ext import db
from google.appengine.ext import ndb
from google.appengine.api import users
from webapp2_extras import sessions
from google.appengine.api import memcache
from SecurityUtils import AccessOK
from DButils import TemplateClone

from models import Templates
from models import TokenValues

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'templates')
jinja_environment = \
    jinja2.Environment(loader=jinja2.FileSystemLoader(TEMPLATE_DIR))
jinja_environment.filters['AccessOK'] = AccessOK

class TemplateBaseHandler(webapp2.RequestHandler):

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


class TemplateList(TemplateBaseHandler):

    def get(self):
#        TemplateClone()
        templates = Templates.query().order(Templates.Name)

        if self.request.get('extyp'):
            extyp=self.request.get('extyp')
            self.session['extyp'] = extyp
        else:
            extyp = self.session.get('extyp')
        if not extyp:
            self.session['extyp'] = 'exercise'

        logout = None
        login = None
        currentuser = users.get_current_user()
        if currentuser:
              logout = users.create_logout_url('/templates' )
        else:
              login = users.create_login_url('/templates/create')
        self.render_template('TemplateList.html', {'templates': templates,'currentuser':currentuser, 'login':login, 'logout': logout})


class TemplateCreate(TemplateBaseHandler):

    def post(self):
        #logging.error('QQQ: templatecreate POST')
        n = Templates(Name=self.request.get('Name')
                  , TemplateType=self.request.get('TemplateType')
                  , FolderName=self.request.get('FolderName')
                  , FileName=self.request.get('FileName')
                  , Description=self.request.get('Description')
                  , Status=self.request.get('Status')
                  )
        n.put()
        return webapp2.redirect('/templates')

    def get(self):
        logout = None
        login = None
        currentuser = users.get_current_user()
        if currentuser:
              logout = users.create_logout_url('/templates' )
        else:
              login = users.create_login_url('/templates/create')

        FolderList = ['exercises', 'utils', 'other'];		  
        StatusList = ['Pending Translation', 'Pending Review', 'Published'];		  
        TemplateTypeList = ['template', 'pagecontent', 'function', 'exercise'];	
        self.render_template('TemplateCreate.html', {'FolderList': FolderList, 'StatusList': StatusList, 'TemplateTypeList': TemplateTypeList, 'currentuser':currentuser, 'login':login, 'logout': logout})


class TemplateEdit(TemplateBaseHandler):

    def post(self, template_id):
        iden = int(template_id)
        template = ndb.Key('Templates', iden).get()
        currentuser = users.get_current_user()
#        if currentuser != template.CreatedBy and not users.is_current_user_admin():
#            self.abort(403)
#            return
        template.Name = self.request.get('Name')
        template.TemplateType = self.request.get('TemplateType')
        template.FolderName=self.request.get('FolderName')
        template.FileName = self.request.get('FileName')
        template.Description = self.request.get('Description')
        StatusPrev = template.Status
        template.Status = self.request.get('Status')
        if not template.Status == StatusPrev:
            template.StatusBy = currentuser
            template.StatusDate = datetime.now()    
        template.put()
        return webapp2.redirect('/templates')

    def get(self, template_id):
        iden = int(template_id)
        template = ndb.Key('Templates', iden).get()
        logout = None
        login = None
        currentuser = users.get_current_user()
        if currentuser:
              logout = users.create_logout_url('/templates' )
        else:
              login = users.create_login_url('/templates')
        FolderList = ['exercises', 'utils', 'try', 'other'];		  
        StatusList = ['Pending Translation', 'Pending Review', 'Published'];		  
        TemplateTypeList = ['template', 'pagecontent', 'function', 'exercise'];	
        self.render_template('TemplateEdit.html', {'template': template, 'FolderList': FolderList, 'StatusList': StatusList, 'TemplateTypeList': TemplateTypeList, 'currentuser':currentuser, 'login':login, 'logout': logout})


class TemplateDelete(TemplateBaseHandler):

    def get(self, template_id):
        iden = int(template_id)
        template = ndb.Key('Templates', iden).get()
        currentuser = users.get_current_user()
#        if currentuser != template.CreatedBy and not users.is_current_user_admin():
#            self.abort(403)
#            return
        template.key.delete()
        return webapp2.redirect('/templates')


