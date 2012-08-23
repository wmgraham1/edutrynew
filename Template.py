import jinja2
import os
import webapp2
from datetime import datetime
from google.appengine.ext import db
from google.appengine.ext import ndb
from google.appengine.api import users
from Security import AccessOK

from models import Templates

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


class TemplateList(TemplateBaseHandler):

    def get(self):
        templates = Templates.query()

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

        StatusList = ['Pending Translation', 'Pending Review', 'Published'];		  
        TemplateTypeList = ['template', 'pagecontent', 'function', 'exercise'];	
        self.render_template('TemplateCreate.html', {'StatusList': StatusList, 'TemplateTypeList': TemplateTypeList, 'currentuser':currentuser, 'login':login, 'logout': logout})


class TemplateEdit(TemplateBaseHandler):

    def post(self, template_id):
        iden = int(template_id)
        template = ndb.Key('Templates', iden).get()
        currentuser = users.get_current_user()
        if currentuser != template.CreatedBy and not users.is_current_user_admin():
            self.abort(403)
            return
        template.Name = self.request.get('Name')
        template.TemplateType = self.request.get('TemplateType')
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
        currentuser = users.get_current_user()
        if currentuser != template.CreatedBy and not users.is_current_user_admin():
            self.abort(403)
            return
        logout = None
        login = None
        currentuser = users.get_current_user()
        if currentuser:
              logout = users.create_logout_url('/templates' )
        else:
              login = users.create_login_url('/templates')
        StatusList = ['Pending Translation', 'Pending Review', 'Published'];		  
        TemplateTypeList = ['template', 'pagecontent', 'function', 'exercise'];	
        self.render_template('TemplateEdit.html', {'template': template, 'StatusList': StatusList, 'TemplateTypeList': TemplateTypeList, 'currentuser':currentuser, 'login':login, 'logout': logout})


class TemplateDelete(TemplateBaseHandler):

    def get(self, template_id):
        iden = int(template_id)
        template = ndb.Key('Templates', iden).get()
        currentuser = users.get_current_user()
        if currentuser != template.CreatedBy and not users.is_current_user_admin():
            self.abort(403)
            return
        template.key.delete()
        return webapp2.redirect('/templates')
