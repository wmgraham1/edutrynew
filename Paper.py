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

    def get(self):
        languages = memcache.get("languages")
        if languages is not None:
           logging.info("get languages from memcache.")
        else:
           languages = Languages.all()
           logging.info("Can not get languages from memcache.")
           if not memcache.add("languages", languages, 10):
               logging.info("Memcache set failed.")

        if self.request.get('langCode'):
            langCode=self.request.get('langCode')
            self.session['langCode'] = langCode
        else:
            langCode = self.session.get('langCode')
        if not langCode:
            self.session['langCode'] = 'en'

        LangName = 'no language'
        for language in languages:
            if language.langCode == langCode:
                langName = language.langName

#        q = db.GqlQuery("SELECT * FROM PageContents " + 
#                "WHERE langCode = :1 " +
#                "ORDER BY TemplateName ASC",
#                "en")
#        pagecontents = q.fetch(999)
		papers = Papers.all()
		#pagecontents = 'xxx'
 
        logout = None
        login = None
        currentuser = users.get_current_user()
        if currentuser:
              logout = users.create_logout_url('/pagecontents' )
        else:
              login = users.create_login_url('/pagecontents/create')
#        self.render_template('PageContentList.html', {'pagecontents': pagecontents, 'LangName':LangName, 'currentuser':currentuser, 'login':login, 'logout': logout})
        self.render_template('PaperList.html', {'papers': papers, 'currentuser':currentuser, 'login':login, 'logout': logout})


class PaperCreate(BaseHandler):

    def post(self):
        logging.info('QQQ: PaperCreate POST')
        #return webapp2.redirect('/papers')
        CreatedBy = users.get_current_user()
	
        n = Papers(Title=self.request.get('Title'),
                Category=self.request.get('Category'),
                Text=self.request.get('Text'),
                Status=self.request.get('Status'),
                CreatedBy=CreatedBy,
                StatusBy=CreatedBy
                )

        logging.info('QQQ: PaperCreate before put')
        n.put()
        logging.info('QQQ: PaperCreate after put')

#<<<<<<< HEAD
        # x = webapp2.redirect('/pagecontents/')
        x = self.redirect('/papers')
        logging.info('QQQ: x: %s' % x)
        return x
#=======
#       return webapp2.redirect('/pagecontents')
#       #return webapp2.redirect('/templates')

#>>>>>>> 0a84a8345dcf5aeb86cca24885ee2d44be5ffce1

    def get(self):
        StatusList = ['Pending Translation', 'Pending Review', 'Published'];
        CategoryList = ['Goals', 'Learning Resources', 'Learning Platform', 'Winning Students', 'Recruiting Volunteers'];
        self.render_template('PaperCreate.html', {'StatusList': StatusList, 'CategoryList': CategoryList})

class PaperDisplay(BaseHandler):

    def get(self, paper_id):
        iden = int(paper_id)
        Paper = db.get(db.Key.from_path('Papers', iden))

        q = Comments.all()
        q.filter("RefObjType =", "paper")
        q.filter("RefObjID =", paper_id)
        q.order("CommentCode")

        logging.info('QQQ: Comment Paper Display before fetch')

        comments = q.fetch(99)

#        commentlist = {}
#        i = -1
#        for commenty in comments:
#            i = i + 1
#            commentlist[commenty.CommentCode] = len(commenty.CommentCode)

        template_values = {
            'Paper': Paper, 
            'Comments': comments,
#            'CommentList': commentlist,
			'iden': iden
            }

        #TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'templates')
        jinja_environment = \
            jinja2.Environment(autoescape=False, loader=jinja2.FileSystemLoader(TEMPLATE_DIR))

        template = jinja_environment.get_template('PaperDisplay.html')
        self.response.out.write(template.render(template_values))

        #StatusList = ['Pending Translation', 'Pending Review', 'Published'];
        #CategoryList = ['Goals', 'Learning Resources', 'Learning Platform', 'Winning Students', 'Recruiting Volunteers'];
        #self.render_template('PaperEdit.html', {'Paper': Paper, 'StatusList': StatusList, 'CategoryList': CategoryList})
        #self.render_template('PaperDisplay.html', {'Paper': Paper})

class PaperEdit(BaseHandler):

    def post(self, paper_id):
        iden = int(paper_id)
        paper = db.get(db.Key.from_path('Papers', iden))
        currentuser = users.get_current_user()
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
        return self.redirect('/papers')

    def get(self, paper_id):
        iden = int(paper_id)
        Paper = db.get(db.Key.from_path('Papers', iden))
        StatusList = ['Pending Translation', 'Pending Review', 'Published'];
        CategoryList = ['Goals', 'Learning Resources', 'Learning Platform', 'Winning Students', 'Recruiting Volunteers'];
        self.render_template('PaperEdit.html', {'Paper': Paper, 'StatusList': StatusList, 'CategoryList': CategoryList})

class PaperDelete(BaseHandler):

    def get(self, paper_id):
        iden = int(paper_id)
        paper = db.get(db.Key.from_path('Papers', iden))
        db.delete(paper)
        return self.redirect('/papers')
