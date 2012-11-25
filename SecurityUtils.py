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

from models import UserSuppl

#class BaseHandler(webapp2.RequestHandler):

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

def AccessOK(xCurrentUser, PermissionID):
#    PermissionID = int(PermID)
    currentuser = users.get_current_user()
    logging.info('GGG: PermissionID: %s' % PermissionID)
    logging.info('GGG: current_user_admin: %s' % users.is_current_user_admin())
    IsOK = False
    if users.is_current_user_admin():
        logging.info('GGG: AccessOKNew-Where: %s' % 'In user is Admin user')
        IsOK = True
    else:
        logging.info('GGG: AccessOKNew-Where: %s' % 'In user is Admin user ELSE')
        q = UserSuppl.query(UserSuppl.UserID == currentuser)
        user = q.get()
        if user:
            logging.info('GGG: AccessOKNew-Where: %s' % 'retrieveD UserSuppl')
            logging.info('GGG: UserID: %s' % user.UserID)
            logging.info('GGG: Role: %s' % user.Role)
            if user.Status == 'Assigned':
                if user.Role == 'admin':
                    IsOK = True
                else:
                    if PermissionID in user.Permissions:
                        IsOK = True
#    IsOK = True
#    logging.info('GGG: Final IsOK: %s' % IsOK)
    logging.info('GGG: AccessOKNew-Just before Rtn: %s' % IsOK)
    return IsOK

class AccessOKNew(BaseHandler):
    def AccessOKNew(Session, PermissionID):
        currentuser = users.get_current_user()
        logging.info('SSS: PermissionID: %s' % PermissionID)
        logging.info('SSS: current_user_admin: %s' % users.is_current_user_admin())
        IsOK = False
        if users.is_current_user_admin():
            logging.info('SSS: AccessOKNew-Where: %s' % 'user is Admin user')
            IsOK = True
        else:
            logging.info('SSS: AccessOKNew-Where: %s' % 'user is Admin user ELSE')
            UserSuppl = session.get('UserSuppl')
            if UserSuppl:
                logging.info('ZZZ: AccessOKNew-Where1: %s' % 'Got UserSuppl from Session')
                if PermissionID in UserSuppl.Permissions:
                    logging.info('SSS: AccessOKNew-Where: %s' % 'Got UserSuppl from Session AND PermissionID is in UserSuppl-Permissions')
                    IsOK = True
            else:
                logging.info('ZZZ: AccessOKNew-Where2: %s' % 'UserSuppl NOT in Session')
                q = UserSuppl.query(UserSuppl.UserID == currentuser)
                UserSuppl = q.get()
                if UserSuppl:
                    logging.info('SSS: AccessOKNew-Where: %s' % 'retrieveD2 UserSuppl')
                    logging.info('SSS: UserID: %s' % UserSuppl.UserID)
                    logging.info('SSS: Role: %s' % UserSuppl.Role)
                    session['UserSuppl'] = UserSuppl
                    if UserSuppl.Status == 'Assigned':
                        logging.info('SSS: AccessOKNew-Where: %s' % 'User status = Assigned')
                        if UserSuppl.Role == 'admin':
                            logging.info('SSS: AccessOKNew-Where: %s' % 'User role = Admin')
                            IsOK = True
                        else:
                            logging.info('SSS: AccessOKNew-Where: %s' % 'User role NOT = Admin')
                            if PermissionID in UserSuppl.Permissions:
                                logging.info('SSS: AccessOKNew-Where: %s' % 'PermissionID in UserSuppl.Permissions')
#                                logging.info('SSS: AccessOKNew-Where: %s' % 'PermissionID in UserSuppl.Permissions')
                                IsOK = True
        logging.info('SSS: AccessOKNew-Just before Rtn: %s' % IsOK)
        return IsOK
