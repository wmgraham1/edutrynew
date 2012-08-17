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

from models import Papers
from models import Comments
from models import Languages

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'templates')
jinja_environment = \
    jinja2.Environment(autoescape=True, loader=jinja2.FileSystemLoader(TEMPLATE_DIR))

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


class PaperList(BaseHandler):

    def get(self, category):
        logging.info("Now in PaperList get.")

        if category == 'resources':
            q = Papers.query(Papers.Category == 'Learning Resources').order(Papers.CreatedDate)
            CatName = 'Learning Resources'
        elif category == 'platform':
            q = Papers.query(Papers.Category == 'Learning Platform').order(Papers.CreatedDate)
            CatName = 'Learning Platform'
        elif category == 'learners':
            q = Papers.query(Papers.Category == 'Winning Students').order(Papers.CreatedDate)
            CatName = 'Learners and Programs'
        elif category == 'misc':
            q = Papers.query(Papers.Category != 'Learning Resources', Papers.Category != 'Learning Platform', Papers.Category != 'Winning Students').order(Papers.Category, Papers.CreatedDate)
            CatName = 'Miscellaneous'
        else:
            q = Papers.query().order(Papers.CreatedDate)
            CatName = 'All'

        papers = q.fetch(99)
		
        logout = None
        login = None
        currentuser = users.get_current_user()
        if currentuser:
              logout = users.create_logout_url('/pagecontents' )
        else:
              login = users.create_login_url('/pagecontents/create')
        self.render_template('PaperList.html', {'papers': papers, 'cat': category, 'CatName': CatName, 'currentuser':currentuser, 'login':login, 'logout': logout})


class PaperDisplay(BaseHandler):

    def get(self, paper_id):
        iden = int(paper_id)
        Paper = ndb.Key('Papers', iden).get()

        q = Comments.query(Comments.RefObjType == 'paper', Comments.RefObjID == paper_id).order(Comments.CommentCode)
        comments = q.fetch(99)

        template_values = {
            'Paper': Paper, 
            'Comments': comments,
			'iden': paper_id
            }

        #TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'templates')
        jinja_environment = \
            jinja2.Environment(autoescape=False, loader=jinja2.FileSystemLoader(TEMPLATE_DIR))

        template = jinja_environment.get_template('PaperDisplay.html')
        self.response.out.write(template.render(template_values))

class PaperCreate(BaseHandler):

    def post(self):
        CreatedBy = users.get_current_user()
        cat=self.request.get('cat')	
        n = Papers(Title=self.request.get('Title'),
                Category=self.request.get('Category'),
                Text=self.request.get('Text'),
                Status=self.request.get('Status'),
                CreatedBy=CreatedBy,
                StatusBy=CreatedBy)
        n.put()

        return self.redirect('/papers/' + cat)

    def get(self):
        cat=self.request.get('cat')	
        logging.info("Now in PaperCreate get.")
        StatusList = ['Pending Translation', 'Pending Review', 'Published'];
        CategoryList = ['Goals', 'Learning Resources', 'Learning Platform', 'Winning Students', 'Volunteers', 'Partnerships/Alliances', 'Wild Ideas'];
        self.render_template('PaperCreate.html', {'StatusList': StatusList, 'cat': cat, 'CategoryList': CategoryList})

class PaperEdit(BaseHandler):

    def post(self, paper_id):
        iden = int(paper_id)
        paper = ndb.Key('Papers', iden).get()
        currentuser = users.get_current_user()
        cat=self.request.get('cat')	
        paper.Title = self.request.get('Title')
        paper.Category = self.request.get('Category')
        paper.Text = self.request.get('Text')
        paper.UpdatedBy = currentuser
        paper.UpdatedDate = datetime.now()
        StatusPrev = paper.Status
        paper.Status = self.request.get('Status')
        if not paper.Status == StatusPrev:
            paper.StatusBy = currentuser
            paper.StatusDate = datetime.now()            
        paper.put()
        return self.redirect('/papers/' + cat)

    def get(self, paper_id):
        iden = int(paper_id)
        Paper = ndb.Key('Papers', iden).get()
        cat=self.request.get('cat')	
        StatusList = ['Pending Translation', 'Pending Review', 'Published'];
        CategoryList = ['Goals', 'Learning Resources', 'Learning Platform', 'Winning Students', 'Volunteers', 'Partnerships/Alliances', 'Wild Ideas'];
        self.render_template('PaperEdit.html', {'Paper': Paper, 'cat': cat, 'StatusList': StatusList, 'CategoryList': CategoryList})

class PaperDelete(BaseHandler):

    def get(self, paper_id):
        iden = int(paper_id)
        cat=self.request.get('cat')	
        paper = ndb.Key('Papers', iden).get()
        paper.key.delete()
        return self.redirect('/papers/' + cat)
