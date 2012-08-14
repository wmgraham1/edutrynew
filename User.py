import jinja2
import os
import webapp2
from datetime import datetime
from google.appengine.ext import db
from google.appengine.ext import ndb
from google.appengine.api import users

from models import UserSuppl

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


class UserList(BaseHandler):

    def get(self):
        user = UserSuppl.query()
        logout = None
        login = None
        currentuser = users.get_current_user()
        if currentuser:
              logout = users.create_logout_url('/templates' )
        else:
              login = users.create_login_url('/templates/create')
        self.render_template('UserList.html', {'user': user, 'currentuser':currentuser, 'login':login, 'logout': logout})


class UserCreate(BaseHandler):

    def post(self):
        #logging.error('QQQ: templatecreate POST')
        currentuser = users.get_current_user()
        n = UserSuppl(FirstName=self.request.get('FirstName')
                  , LastName=self.request.get('LastName')
                  , UserID=currentuser
                  , Descr=self.request.get('Descr')
                  , Status='Pending Assignment'
                  )
        n.put()
        return webapp2.redirect('/users')

    def get(self):
        logout = None
        login = None
        currentuser = users.get_current_user()
        if currentuser:
              logout = users.create_logout_url('/users' )
        else:
              login = users.create_login_url('/users/create')

        self.render_template('UserCreate.html', {'currentuser':currentuser, 'login':login, 'logout': logout})


class UserEdit(BaseHandler):

    def post(self, user_id):
        iden = int(user_id)
        user = ndb.Key('UserSuppl', iden).get()
        currentuser = users.get_current_user()
        user.UserID = self.request.get('UserID')
        user.FirstName = self.request.get('FirstName')
        user.LastName = self.request.get('LastName')
        user.Descr = self.request.get('Descr')
        StatusPrev = user.Status
        user.Status = self.request.get('Status')
        if not user.Status == StatusPrev:
            user.StatusBy = currentuser
            user.StatusDate = datetime.now()    
        user.put()
        return webapp2.redirect('/users')

    def get(self, user_id):
        iden = int(user_id)
        user = ndb.Key('UserSuppl', iden).get()

        logout = None
        login = None
        currentuser = users.get_current_user()
        if currentuser:
              logout = users.create_logout_url('/users' )
        else:
              login = users.create_login_url('/users')
        UserStatusList = ['Pending Assignment', 'Assigned', 'Blocked'];		  
        self.render_template('UserEdit.html', {'user': user, 'StatusList': UserStatusList, 'currentuser':currentuser, 'login':login, 'logout': logout})


class UserDelete(BaseHandler):

    def get(self, user_id):
        iden = int(user_id)
        user = ndb.Key('UserSuppl', iden).get()
        currentuser = users.get_current_user()
#        if currentuser != template.CreatedBy and not users.is_current_user_admin():
#            self.abort(403)
#            return
        user.key.delete()
        return webapp2.redirect('/users')

