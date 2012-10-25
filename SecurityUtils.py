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
#    logging.info('GGG: PermissionID: %s' % PermissionID)
#    logging.info('GGG: current_user_admin: %s' % users.is_current_user_admin())
    IsOK = False
    if users.is_current_user_admin():
        IsOK = True
    else:
        q = UserSuppl.query(UserSuppl.UserID == currentuser)
        user = q.get()
        if user:
#            logging.info('GGG: UserID: %s' % user.UserID)
#            logging.info('GGG: Role: %s' % user.Role)
            if user.Status == 'Assigned':
                if user.Role == 'admin':
                    IsOK = True
                else:
                    if PermissionID in user.Permissions:
                        IsOK = True
#    IsOK = True
#    logging.info('GGG: Final IsOK: %s' % IsOK)
    return IsOK
