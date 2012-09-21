from google.appengine.api import users
from google.appengine.ext import blobstore
from datetime import datetime
from google.appengine.ext import db
from google.appengine.ext import ndb
from google.appengine.api import users
from webapp2_extras import sessions
from google.appengine.api import memcache
from SecurityUtils import AccessOK
from google.appengine.ext import webapp
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp import util

import jinja2
import os
import webapp2
import logging

from models import SubjectAreas
from models import Languages

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'templates')
jinja_environment = \
    jinja2.Environment(loader=jinja2.FileSystemLoader(TEMPLATE_DIR))
jinja_environment.filters['AccessOK'] = AccessOK

class FileInfo(ndb.Model):
    blob = ndb.BlobKeyProperty(required=True)
    uploaded_by = ndb.UserProperty(required=True)
    uploaded_at = ndb.DateTimeProperty(required=True, auto_now_add=True)

class BaseHandler(webapp.RequestHandler):
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

#    def render_template(self, file, template_args):
#        path = os.path.join(os.path.dirname(__file__), "templates", file)
#        self.response.out.write(template.render(path, template_args))

class FileUploadFormHandler(BaseHandler):
#    @util.login_required
    def get(self):
        self.render_template("FileUpload.html", {
            'form_url': blobstore.create_upload_url('/files/upload')#,
#            'logout_url': users.create_logout_url('/files'),
            })
#        self.render_template('GenFileList.html', {'genfiles': genfiles, 'currentuser':currentuser, 'login':login, 'logout': logout})

class FileUploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        blob_info = self.get_uploads()[0]
        if not users.get_current_user():
            blob_info.delete()
            self.redirect(users.create_login_url("/files"))
            return
        file_info = FileInfo(blob=blob_info.key(),
            uploaded_by=users.get_current_user())
        file_info.put()
#        self.redirect("/files/fileinfo/%d" % (file_info.key.id()))
        self.redirect("/files/fileinfo/" + str(file_info.key.id()))

class FileInfoHandler(BaseHandler):
    def get(self, file_id):
#        file_info = FileInfo.get_by_id(long(file_id))
        iden = int(file_id)
        file_info = ndb.Key('TokenValues', iden).get()
        if not file_info:
            self.error(404)
            return
        self.render_template("FileInfo.html", {
            'file_info': file_info#,
#            'logout_url': users.create_logout_url('/files'),
            })

class FileDownloadHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, file_id):
#        file_info = FileInfo.get_by_id(long(file_id))
        iden = int(file_id)
        file_info = ndb.Key('TokenValues', iden).get()
        if not file_info or not file_info.blob:
            self.error(404)
            return
        self.send_blob(file_info.blob, save_as=True)
