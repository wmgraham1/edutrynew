import jinja2
import os
import webapp2
import logging
from datetime import datetime
from google.appengine.ext import db
from google.appengine.ext import ndb
from webapp2_extras import sessions
from google.appengine.api import memcache
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.api import users
from SecurityUtils import AccessOK

from models import GeneratedFiles

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


class GenFileList(BaseHandler):

    def get(self):
        genfiles = GeneratedFiles.query().order(GeneratedFiles.TemplateName)

        logout = None
        login = None
        currentuser = users.get_current_user()
        if currentuser:
              logout = users.create_logout_url('/genfiles' )
        else:
              login = users.create_login_url('/genfiles')
        jinja_environment = \
            jinja2.Environment(autoescape=False, loader=jinja2.FileSystemLoader(TEMPLATE_DIR))
        self.render_template('GenFileList.html', {'genfiles': genfiles, 'currentuser':currentuser, 'login':login, 'logout': logout})

class GenFileInfoList(BaseHandler):

    def get(self):
        genfiles = GeneratedFiles.query(GeneratedFiles.BlobKey != None).order(GeneratedFiles.BlobKey, GeneratedFiles.TemplateName)

#        genfiles = GeneratedFiles.get()
        
        logout = None
        login = None
        currentuser = users.get_current_user()
        if currentuser:
              logout = users.create_logout_url('/genfiles' )
        else:
              login = users.create_login_url('/genfiles')
        self.render_template('GenFileInfoList.html', {'genfiles': genfiles, 'currentuser':currentuser, 'login':login, 'logout': logout})

class GenFileDisplay(BaseHandler):

    def get(self, genfile_id):
        iden = int(genfile_id)
        genfile = ndb.Key('GeneratedFiles', iden).get()

        if genfile:
            TextOut = genfile.FileTxt.decode('utf-8')
        else:
            TextOut = 'No such file.'
#            genfile = 'No such file.'

        logout = None
        login = None
        currentuser = users.get_current_user()
        if currentuser:
              logout = users.create_logout_url('/templates' )
        else:
              login = users.create_login_url('/templates')
        self.render_template('GenFileDisplay.html', {'genfile': genfile, 'TextOut': TextOut, 'currentuser':currentuser, 'login':login, 'logout': logout})

class GenFileAltDisplay(BaseHandler):

    def get(self):
        TemplateName=self.request.get('TemplateName')
        LangCode=self.request.get('LangCode')
        q = GeneratedFiles.query(GeneratedFiles.LangCode == LangCode, GeneratedFiles.TemplateName == TemplateName).order(GeneratedFiles.LangCode, GeneratedFiles.TemplateName, -GeneratedFiles.CreatedDate)
        genfile = q.get()

        if genfile:
            TextOut = genfile.FileTxt.decode('utf-8')
        else:
            TextOut = 'No such file.'
#            genfile = 'No such file.'
        
        logout = None
        login = None
        currentuser = users.get_current_user()
        if currentuser:
              logout = users.create_logout_url('/templates' )
        else:
              login = users.create_login_url('/templates')
        self.render_template('GenFileDisplay.html', {'genfile': genfile, 'TextOut': TextOut, 'currentuser':currentuser, 'login':login, 'logout': logout})

class GenFileDelete(BaseHandler):

    def get(self, genfile_id):
        iden = int(genfile_id)
        genfile = ndb.Key('GeneratedFiles', iden).get()
        currentuser = users.get_current_user()
#        if currentuser != template.CreatedBy and not users.is_current_user_admin():
#            self.abort(403)
#            return
        genfile.key.delete()
        return self.redirect('/genfiles')

class FileDownloadHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, genfile_id):
        iden = int(genfile_id)
        file_info = ndb.Key('GeneratedFiles', iden).get()
        if not file_info or not file_info.blob:
            self.error(404)
            return
        else:
            blob_info = blobstore.BlobInfo.get(file_info.blob) 
            #blob_info = blobstore.BlobInfo.get(blob_key)
#        logging.info('QQQ: FileDownloadHandler/blob: %s' % blob)
        self.send_blob(blob_info, save_as=True)
#        self.send_blob(blobstore.BlobInfo(file_info.blob), save_as=True)
#        self.send_blob(BlobInfo(blob), save_as=True)
#        self.response.out.write(BlobInfo(blob))

class FileTryHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, genfile_id):
        iden = int(genfile_id)
        file_info = ndb.Key('GeneratedFiles', iden).get()
        if not file_info or not file_info.blob:
            self.error(404)
            return
        redirect_target = "/genfiles/try/" + file_info.LangCode + "/" + file_info.SearchName
        logging.info('QQQ: redirect_target: %s' % redirect_target)
        self.redirect(redirect_target)
#        blob_info = blobstore.BlobInfo.get(file_info.blob)
#        self.send_blob(blob_info, content_type='text/html')

class FileTryHandlerAlt(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, LangCode, TemplateName):
        q = GeneratedFiles.query(GeneratedFiles.LangCode == LangCode, GeneratedFiles.SearchName == TemplateName).order(GeneratedFiles.LangCode, GeneratedFiles.TemplateName, -GeneratedFiles.CreatedDate)
        genfile = q.get()
        if not genfile:
            q2 = GeneratedFiles.query(GeneratedFiles.LangCode == 'en', GeneratedFiles.TemplateName == TemplateName).order(GeneratedFiles.LangCode, GeneratedFiles.TemplateName, -GeneratedFiles.CreatedDate)
            genfile = q2.get()
            if not genfile:
                self.redirect("/try-it/" + TemplateName)
                return
        logging.info('QQQ: FileTryHandlerAlt : %s' % 'just before blob_info get')
        blob_info = blobstore.BlobInfo.get(genfile.blob)
        logging.info('QQQ: FileTryHandlerAlt : %s' % 'just after blob_info get')
        self.send_blob(blob_info, content_type='text/html')
        logging.info('QQQ: FileTryHandlerAlt : %s' % 'just after blob_info send')

class FileTryHandlerAltTry(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, LangCode, TemplateName):
        q = GeneratedFiles.query(GeneratedFiles.LangCode == LangCode, GeneratedFiles.SearchName == TemplateName).order(GeneratedFiles.LangCode, GeneratedFiles.TemplateName, -GeneratedFiles.CreatedDate)
        genfile = q.get()
        if not genfile:
            q2 = GeneratedFiles.query(GeneratedFiles.LangCode == 'en', GeneratedFiles.TemplateName == TemplateName).order(GeneratedFiles.LangCode, GeneratedFiles.TemplateName, -GeneratedFiles.CreatedDate)
            genfile = q2.get()
            if not genfile:
                self.redirect("/try-it/utils/" + TemplateName)
                return
        logging.info('QQQ: FileTryHandlerAlt : %s' % 'just before blob_info get')
        blob_info = blobstore.BlobInfo.get(genfile.blob)
        logging.info('QQQ: FileTryHandlerAlt : %s' % 'just after blob_info get')
        self.send_blob(blob_info, content_type='text/html')
        logging.info('QQQ: FileTryHandlerAlt : %s' % 'just after blob_info send')

class GenFileRedirect(BaseHandler):
    def get(self):
#        self.redirect("/try-it/loader.js")
        if self.request.get('langCode'):
            langCode=self.request.get('langCode')
            self.session['langCode'] = langCode
        else:
            langCode = self.session.get('langCode')
        if not langCode:
            self.session['langCode'] = 'en' 
            langCode = 'en'
        redirect_target = ("/genfiles/try/" + langCode + "/khan-exercise.js")
        logging.info('QQQ: redirect_target: %s' % redirect_target)
        self.redirect(redirect_target)

class GenFileRedirectHints(BaseHandler):
    def get(self):
#        self.redirect("/try-it/loader.js")
        if self.request.get('langCode'):
            langCode=self.request.get('langCode')
            self.session['langCode'] = langCode
        else:
            langCode = self.session.get('langCode')
        if not langCode:
            self.session['langCode'] = 'en' 
            langCode = 'en'
        redirect_target = ("/genfiles/try/utils/" + langCode + "/hints.js")
        logging.info('QQQ: redirect_target-Hints: %s' % redirect_target)
        self.redirect(redirect_target)

