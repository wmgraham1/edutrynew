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
from Security import AccessOK
from jinja2 import Environment, FileSystemLoader

from models import UserSuppl

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'templates')
jinja_environment = \
    jinja2.Environment(loader=jinja2.FileSystemLoader(TEMPLATE_DIR))
jinja_environment.filters['AccessOK'] = AccessOK

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


class UserList(BaseHandler):

    def get(self):

#        env = Environment(loader=FileSystemLoader('tokenizedtemplates'))
#        template = env.get_template('test_template.html')
#        output_from_parsed_template = template.render(content='Hello World!')
        #print output_from_parsed_template

        # to save the results
#        with open("tokenizedtemplates/my_new_file.html", "w") as fh:
#            fh.write(output_from_parsed_template)


#        TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'templates')
#        jinja_environment = \
#            jinja2.Environment(loader=jinja2.FileSystemLoader(TEMPLATE_DIR))

        user = UserSuppl.query()
        logout = None
        login = None
        currentuser = users.get_current_user()
        if currentuser:
              logout = users.create_logout_url('/users' )
        else:
              login = users.create_login_url('/users')
        self.render_template('UserList.html', {'user': user, 'currentuser':currentuser, 'login':login, 'logout': logout})


class UserJoin(BaseHandler):

    def get(self):
        user = UserSuppl.query()
        logout = None
        login = None
        currentuser = users.get_current_user()
        if currentuser:
            logout = users.create_logout_url('/users/join' )
            UserRegOK = 'Y'
        else:
            login = users.create_login_url('/users/join')
            UserRegOK = 'N'
        self.render_template('UserJoin.html', {'UserRegOK': UserRegOK, 'currentuser':currentuser, 'login':login, 'logout': logout})


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
        return self.redirect('/users')

    def get(self):
        logout = None
        login = None
        currentuser = users.get_current_user()
        if currentuser:
              logout = users.create_logout_url('/users' )
        else:
              login = users.create_login_url('/users/create')
        q = UserSuppl.query(UserSuppl.UserID == currentuser)
        user = q.get()
        if user:
            return self.redirect('/users/join')
        else:
            self.render_template('UserCreate.html', {'currentuser':currentuser, 'login':login, 'logout': logout})


class UserEdit(BaseHandler):

    def post(self, user_id):
        iden = int(user_id)
        user = ndb.Key('UserSuppl', iden).get()
#        UserID = self.session.get('UserID')
        currentuser = users.get_current_user()
#        user.UserID = UserID   #self.request.get('UserID')
#        user.UserID = self.request.get('UserIDx')
        user.FirstName = self.request.get('FirstName')
        user.LastName = self.request.get('LastName')
        user.Role = self.request.get('Role')
        user.Descr = self.request.get('Descr')
        StatusPrev = user.Status
        user.Status = self.request.get('Status')
        if not user.Status == StatusPrev:
            user.StatusBy = currentuser
            user.StatusDate = datetime.now()    
        user.put()
        return self.redirect('/users')

    def get(self, user_id):
        iden = int(user_id)
        user = ndb.Key('UserSuppl', iden).get()
        login = None
        currentuser = users.get_current_user()
        if currentuser:
              logout = users.create_logout_url('/users' )
        else:
              login = users.create_login_url('/users')
        UserStatusList = ['Pending Assignment', 'Assigned', 'Blocked'];		  
        RoleList = ['admin', 'advocate', 'tokentranslator'];		  
        self.render_template('UserEdit.html', {'user': user, 'StatusList': UserStatusList, 'RoleList': RoleList, 'currentuser':currentuser, 'login':login, 'logout': logout})


class UserRightsCalc(BaseHandler):

    def get(self, role_id):
        RoleListAdvocate = [110,111,120, 121, 210, 211, 220, 221, 230, 231, 232];
        RoleListTokenBuilder = [110,111,120, 121, 210, 211, 220, 221, 230, 231, 232];
        RoleListTokenTranslator = [110,111,120, 121, 210, 220, 230, 231, 232];
        RolePermissionDict = {}
        RolePermissionDict['advocate'] = RoleListAdvocate
        RolePermissionDict['tokenbuilder'] = RoleListTokenBuilder
        RolePermissionDict['tokentranslator'] = RoleListTokenTranslator
        RolePermissionsList =  RolePermissionDict[role_id]

        q = UserSuppl.query(UserSuppl.Role == role_id, UserSuppl.Status == 'Assigned')
        userx = q.fetch(999)

        currentuser = users.get_current_user()
        logging.info('QQQ: currentuser: %s' % currentuser)

        for user in userx:
            logging.info('QQQ: UserID: %s' % user.UserID)
            logging.info('QQQ: Role: %s' % user.Role)
            PermissionsPrev = user.Permissions
            user.Permissions = RolePermissionsList
            if not user.Permissions == PermissionsPrev:
                user.ChangedBy = currentuser
                user.ChangedDate = datetime.now() 			
            StatusPrev = user.Status
            user.Status = self.request.get('Status')
            if not user.Status == StatusPrev:
                user.StatusBy = currentuser
                user.StatusDate = datetime.now()    
            user.put()

#        if currentuser != template.CreatedBy and not users.is_current_user_admin():
#            self.abort(403)
#            return
        return self.redirect('/admin/roles/display/' + role_id)
		
class UserDelete(BaseHandler):

    def get(self, user_id):
        iden = int(user_id)
        user = ndb.Key('UserSuppl', iden).get()
        currentuser = users.get_current_user()
#        if currentuser != template.CreatedBy and not users.is_current_user_admin():
#            self.abort(403)
#            return
        user.key.delete()
        return self.redirect('/users')


class PermissionTest(BaseHandler):

    def get(self):
        logging.info('QQQ: Start of Permission Test')
        PermissionID = 225
        Rslt = 'X'
#        if AccessOK(PermissionID):
#            Rslt = 'Y'
#        else:
#            Rslt = 'N'
        IsOK = AccessOK(PermissionID)
#        total = sum( 10, 20 );
#        logging.info('QQQ: results for total: %d' % total)
#        print "Outside the function : ", total 

#        xyz = fadd()
#        currentuser = users.get_current_user()
#        user = ndb.Key('UserSuppl', iden).get()
#        logging.info('QQQ: results for xyz: %s' % xyz)
#        print 'Result: ', fadd()
        self.render_template('AccessTest.html', {'PermissionID': PermissionID, 'IsOK': IsOK})

