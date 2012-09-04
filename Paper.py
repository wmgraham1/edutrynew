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
from SecurityUtils import AccessOK

from models import Papers
from models import Comments
from models import Languages

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'templates')
jinja_environment = \
    jinja2.Environment(autoescape=True, loader=jinja2.FileSystemLoader(TEMPLATE_DIR))
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
            q = Papers.query(Papers.Category != 'Feedback', Papers.Category != 'Learning Resources', Papers.Category != 'Learning Platform', Papers.Category != 'Winning Students').order(Papers.Category, Papers.CreatedDate)
            CatName = 'Miscellaneous'
        else:
            q = Papers.query().order(Papers.Category, Papers.CreatedDate)
            CatName = 'All'

        papers = q.fetch(99)

        if papers:
            Havepapers = True
        else:
            Havepapers = False
		
        logout = None
        login = None
        currentuser = users.get_current_user()
        if currentuser:
              logout = users.create_logout_url('/pagecontents' )
        else:
              login = users.create_login_url('/pagecontents/create')
        self.render_template('PaperList.html', {'papers': papers, 'Havepapers': Havepapers, 'cat': category, 'CatName': CatName, 'currentuser':currentuser, 'login':login, 'logout': logout})

class FeedbackList(BaseHandler):

    def get(self):
        logging.info("Now in FeedbackList get.")
        CatName = 'All'

        q = Papers.query(Papers.Category == 'Feedback').order(-Papers.CreatedDate)
        papers = q.fetch(999)
        
        if papers:
            Havepapers = True
        else:
            Havepapers = False
		
        logout = None
        login = None
        currentuser = users.get_current_user()
        if currentuser:
              logout = users.create_logout_url('/feedback' )
        else:
              login = users.create_login_url('/feedback')

        template_values = {
            'papers': papers, 
            'Havepapers': Havepapers,
            'currentuser':currentuser, 
            'login':login, 
            'logout': logout
            }

        jinja_environment = \
            jinja2.Environment(autoescape=False, loader=jinja2.FileSystemLoader(TEMPLATE_DIR))
        jinja_environment.filters['AccessOK'] = AccessOK

        template = jinja_environment.get_template('FeedbackList.html')
        self.response.out.write(template.render(template_values))

#        self.render_template('FeedbackList.html', {'papers': papers, 'Havepapers': Havepapers, 'currentuser':currentuser, 'login':login, 'logout': logout})


class PaperDisplay(BaseHandler):

    def get(self, paper_id):
        iden = int(paper_id)
        Paper = ndb.Key('Papers', iden).get()

        q = Comments.query(Comments.RefObjType == 'paper', Comments.RefObjID == paper_id).order(Comments.CommentCode)
        comments = q.fetch(99)

        logout = None
        login = None
        currentuser = users.get_current_user()
        if currentuser:
              logout = users.create_logout_url('/paper/display' )
        else:
              login = users.create_login_url('/paper/display')

        template_values = {
            'Paper': Paper, 
            'Comments': comments,
			'iden': paper_id,
            'currentuser':currentuser, 
            'login':login, 
            'logout': logout
            }

        #TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'templates')
        jinja_environment = \
            jinja2.Environment(autoescape=False, loader=jinja2.FileSystemLoader(TEMPLATE_DIR))

        template = jinja_environment.get_template('PaperDisplay.html')
        jinja_environment.filters['AccessOK'] = AccessOK
        self.response.out.write(template.render(template_values))

class FeedbackDisplay(BaseHandler):

    def get(self, paper_id):
        iden = int(paper_id)
        Paper = ndb.Key('Papers', iden).get()

        q = Comments.query(Comments.RefObjType == 'paper', Comments.RefObjID == paper_id).order(Comments.CommentCode)
        comments = q.fetch(99)

        logout = None
        login = None
        currentuser = users.get_current_user()
        if currentuser:
              logout = users.create_logout_url('/feedback/display' )
        else:
              login = users.create_login_url('/feedback/display')

        template_values = {
            'Paper': Paper, 
            'Comments': comments,
			'iden': paper_id,
            'currentuser':currentuser, 
            'login':login, 
            'logout': logout
            }

        #TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'templates')
#        jinja_environment = \
#            jinja2.Environment(autoescape=False, loader=jinja2.FileSystemLoader(TEMPLATE_DIR))

        template = jinja_environment.get_template('FeedbackDisplay.html')
#        jinja_environment.filters['AccessOK'] = AccessOK
        self.response.out.write(template.render(template_values))

class PaperCreate(BaseHandler):

    def post(self):
        CreatedBy = users.get_current_user()
        cat=self.request.get('cat')	
        n = Papers(Title=self.request.get('Title'),
                Category=self.request.get('Category'),
                Text=self.request.get('Text'),
                Type=self.request.get('Type'),
                Status=self.request.get('Status'),
                CreatedBy=CreatedBy,
                StatusBy=CreatedBy)
        n.put()

        return self.redirect('/papers/' + cat)

    def get(self):
        cat=self.request.get('cat')	
        logging.info("Now in PaperCreate get.")

        logout = None
        login = None
        currentuser = users.get_current_user()
        if currentuser:
              logout = users.create_logout_url('/tokens' )
        else:
              login = users.create_login_url('/tokens')

        StatusList = ['Published', 'Pending Review'];
        TypeList = ['Discussion Paper', 'Question/Problem', 'Experience Report'];
        CategoryList = ['Goals', 'Learning Resources', 'Learning Platform', 'Winning Students', 'Volunteers', 'Partnerships/Alliances', 'Wild Ideas'];
        self.render_template('PaperCreate.html', {'StatusList': StatusList, 'TypeList': TypeList, 'cat': cat, 'CategoryList': CategoryList, 'currentuser':currentuser, 'login':login, 'logout': logout})

class FeedbackCreate(BaseHandler):

    def post(self):
        CreatedBy = users.get_current_user()
        n = Papers(
            Title=self.request.get('Title'),
            Category='Feedback',
            Text=self.request.get('Text'),
            Type='Feedback',
            Status='Published',
            CreatedBy=CreatedBy,
            StatusBy=CreatedBy)
        logging.info('QQQ: FeedbackPost_Title: %s' % n.Title)
        logging.info('QQQ: FeedbackPost_Category: %s' % n.Category)
        logging.info('QQQ: FeedbackPost_Text: %s' % n.Text)
        logging.info('QQQ: FeedbackPost_Type: %s' % n.Type)
        logging.info('QQQ: FeedbackPost_Status: %s' % n.Status)
        n.put()

        return self.redirect('/feedback')

    def get(self):
        cat=self.request.get('cat')	
        logging.info("Now in PaperCreate get.")
        self.render_template('FeedbackCreate.html', {'cat': cat})

class PaperEdit(BaseHandler):

    def post(self, paper_id):
        iden = int(paper_id)
        paper = ndb.Key('Papers', iden).get()
        currentuser = users.get_current_user()
        cat=self.request.get('cat')	
        logging.info('QQQ: PaperEdit_cat: %s' % cat)
        paper.Title = self.request.get('Title')
        paper.Category = self.request.get('Category')
        paper.Category = self.request.get('Type')
        paper.Text = self.request.get('Text')
        paper.UpdatedBy = currentuser
        paper.UpdatedDate = datetime.now()
        StatusPrev = paper.Status
        paper.Status = self.request.get('Status')
        if not paper.Status == StatusPrev:
            paper.StatusBy = currentuser
            paper.StatusDate = datetime.now()            
        paper.put()
        logging.info('QQQ: PaperEdit_cat: %s' % cat)
        return self.redirect('/papers/' + cat)

    def get(self, paper_id):
        iden = int(paper_id)
        Paper = ndb.Key('Papers', iden).get()
        cat=self.request.get('cat')	

        logout = None
        login = None
        currentuser = users.get_current_user()
        if currentuser:
              logout = users.create_logout_url('/tokens' )
        else:
              login = users.create_login_url('/tokens')

        TypeList = ['Discussion Paper', 'Question/Problem', 'Experience Report'];
        StatusList = ['Published', 'Pending Review'];
        CategoryList = ['Goals', 'Learning Resources', 'Learning Platform', 'Winning Students', 'Volunteers', 'Partnerships/Alliances', 'Wild Ideas', 'Feedback'];
        self.render_template('PaperEdit.html', {'Paper': Paper, 'cat': cat, 'StatusList': StatusList, 'CategoryList': CategoryList, 'TypeList': TypeList, 'currentuser':currentuser, 'login':login, 'logout': logout})

class FeedbackEdit(BaseHandler):

    def post(self, paper_id):
        iden = int(paper_id)
        paper = ndb.Key('Papers', iden).get()
        currentuser = users.get_current_user()
        cat=self.request.get('cat')	
        paper.Title = self.request.get('Title')
        paper.Category = 'Feedback'
        paper.Text = self.request.get('Text')
        paper.Type = 'Feedback'
        paper.UpdatedBy = currentuser
        paper.UpdatedDate = datetime.now()
        StatusPrev = paper.Status
        paper.Status = self.request.get('Status')
        if not paper.Status == StatusPrev:
            paper.StatusBy = currentuser
            paper.StatusDate = datetime.now()            
        paper.put()
        return self.redirect('/feedback')

    def get(self, paper_id):
        iden = int(paper_id)
        Paper = ndb.Key('Papers', iden).get()
        cat=self.request.get('cat')	
        StatusList = ['Published', 'Pending Review'];
        CategoryList = ['Goals', 'Learning Resources', 'Learning Platform', 'Winning Students', 'Volunteers', 'Partnerships/Alliances', 'Wild Ideas', 'Feedback'];
        self.render_template('FeedbackEdit.html', {'Paper': Paper, 'cat': cat, 'StatusList': StatusList, 'CategoryList': CategoryList})

class PaperDelete(BaseHandler):

    def get(self, paper_id):
        iden = int(paper_id)
        cat=self.request.get('cat')	
        paper = ndb.Key('Papers', iden).get()
        paper.key.delete()
        return self.redirect('/papers/' + cat)
