import jinja2
import os
import webapp2
from datetime import datetime
from google.appengine.ext import db
from google.appengine.api import users
from Security import AccessOK

from models import Notes

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


class MainPage(BaseHandler):

    def get(self):
        notes = Notes.all()
        logout = None
        login = None
        currentuser = users.get_current_user()
        if currentuser:
              logout = users.create_logout_url('/notes' )
        else:
              login = users.create_login_url('/notes/create')
        self.render_template('index.html', {'notes': notes,'currentuser':currentuser, 'login':login, 'logout': logout})


class CreateNote(BaseHandler):

    def post(self):
        n = Notes(author=self.request.get('author'),
                  text=self.request.get('text'),
                  priority=self.request.get('priority'),
                  status=self.request.get('status')
                  , whichuser=users.get_current_user()
                  )

        n.put()
        return webapp2.redirect('/notes')

    def get(self):
        logout = None
        login = None
        currentuser = users.get_current_user()
        if currentuser:
              logout = users.create_logout_url('/notes' )
        else:
              login = users.create_login_url('/notes/create')
        self.render_template('create.html', {'currentuser':currentuser, 'login':login, 'logout': logout})


class EditNote(BaseHandler):

    def post(self, note_id):
        iden = int(note_id)
        note = db.get(db.Key.from_path('Notes', iden))
        currentuser = users.get_current_user()
        if currentuser != note.whichuser and not users.is_current_user_admin():
            self.abort(403)
            return
        note.author = self.request.get('author')
        note.text = self.request.get('text')
        note.priority = self.request.get('priority')
        note.status = self.request.get('status')
        note.date = datetime.now()
        note.put()
        return webapp2.redirect('/notes')

    def get(self, note_id):
        iden = int(note_id)
        note = db.get(db.Key.from_path('Notes', iden))
        currentuser = users.get_current_user()
        if currentuser != note.whichuser and not users.is_current_user_admin():
            self.abort(403)
            return
        logout = None
        login = None
        currentuser = users.get_current_user()
        if currentuser:
              logout = users.create_logout_url('/notes' )
        else:
              login = users.create_login_url('/notes')
        self.render_template('edit.html', {'note': note,'currentuser':currentuser, 'login':login, 'logout': logout})


class DeleteNote(BaseHandler):

    def get(self, note_id):
        iden = int(note_id)
        note = db.get(db.Key.from_path('Notes', iden))
        currentuser = users.get_current_user()
        if currentuser != note.whichuser and not users.is_current_user_admin():
            self.abort(403)
            return
        db.delete(note)
        return webapp2.redirect('/notes')
