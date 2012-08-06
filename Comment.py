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


class CommentList(BaseHandler):

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

		#comments = Comments.all()
		#pagecontents = 'xxx'

        q = Comments.all()
        #q.filter("RefObjType =", "paper")
        #q.filter("RefObjID =", iden)
        #q.order("CommentCode")

        logging.info('QQQ: Comment Comment List before fetch')

        comments = q.fetch(99)

		
        logout = None
        login = None
        currentuser = users.get_current_user()
        if currentuser:
              logout = users.create_logout_url('/comments' )
        else:
              login = users.create_login_url('/comments')
#        self.render_template('PageContentList.html', {'pagecontents': pagecontents, 'LangName':LangName, 'currentuser':currentuser, 'login':login, 'logout': logout})
        self.render_template('CommentList.html', {'Comments': comments, 'currentuser':currentuser, 'login':login, 'logout': logout})


class CommentCreate(BaseHandler):

    def post(self, paper_id):
        logging.info('QQQ: Comment Create POST')

        RefObjID=self.request.get('RefObjID')
        CreatedBy = users.get_current_user()

        q = Comments.all()
        q.filter("RefObjType =", "paper")
        q.filter("RefObjID =", RefObjID)
        q.order("-CommentCode")

        comments = q.get()

        CommentMax = chr(ord('A') - 1)

#        for comment in comments:
#            if len(comment.CommentCode) == 1:
#                if comment.CommentCode > CommentMax:
#                    CommentMax = comment.CommentCode

        if comments.CommentCode:
            CommentCodeX = chr(ord(comments.CommentCode[0]) + 1)
        else:
            CommentCodeX = 'A'

        n = Comments(Title=self.request.get('Title'),
                RefObjType=self.request.get('RefObjType'),
                RefObjID=RefObjID,
                CommentCode=CommentCodeX,
                Text=self.request.get('Text'),
#                Status=self.request.get('Status'),
                CreatedBy=CreatedBy#,
#                StatusBy=CreatedBy
                )

        logging.info('QQQ: Comment Create before put')
        n.put()
        logging.info('QQQ: Comment Create after put')

        x = self.redirect('/papers')
        logging.info('QQQ: Comment Create calc x')
        logging.info('QQQ: x: %s' % x)
        return x

    def get(self, paper_id):
        iden = int(paper_id)
        Paper = db.get(db.Key.from_path('Papers', iden))
        RefObjType = 'paper'
        RefObjID = paper_id
        mgnwidth = 0

        StatusList = ['Pending Translation', 'Pending Review', 'Published'];
        CategoryList = ['Goals', 'Learning Resources', 'Learning Platform', 'Winning Students', 'Recruiting Volunteers'];

        jinja_environment = \
            jinja2.Environment(autoescape=False, loader=jinja2.FileSystemLoader(TEMPLATE_DIR))

        template_values = {
            'Comment': Paper, 
            'RefObjType': RefObjType,
            'RefObjID': RefObjID,
            'StatusList': StatusList,
            'CategoryList': CategoryList,
            'mgnwidth': mgnwidth
            }

        #TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'templates')
        jinja_environment = \
            jinja2.Environment(autoescape=False, loader=jinja2.FileSystemLoader(TEMPLATE_DIR))

        template = jinja_environment.get_template('CommentCreate.html')
        self.response.out.write(template.render(template_values))
			
#        self.render_template('CommentCreate.html', {'Comment': Paper, 'RefObjType': RefObjType, 'RefObjID': RefObjID, 'StatusList': StatusList, 'CategoryList': CategoryList})

class CommentSubCreate(BaseHandler):

    def post(self, comment_id):
        iden = int(comment_id)
        Comment = db.get(db.Key.from_path('Comments', iden))
        logging.info('QQQ: CommentSub Create POST')

        RefObjID=self.request.get('RefObjID')


        q = Comments.all()
        q.filter("RefObjType =", "paper")
        q.filter("RefObjID =", RefObjID)
        q.order("-CommentCode")

        comments = q.fetch(99)

        CommentCodeLen = len(Comment.CommentCode)
        logging.info('QQQ: CommentCodeLen: %d' % CommentCodeLen)
        commentCodeEndPos = CommentCodeLen
        logging.info('QQQ: commentCodeEndPos: %d' % commentCodeEndPos)

        CommentCodeMax = chr(ord('A') - 1)
        SubCommentCnt = 0
        logging.info('QQQ: SubCommentCnt: %d' % SubCommentCnt)
        logging.info('QQQ: Comment.CommentCode: %s' % Comment.CommentCode)
        for subcomment in comments:
            logging.info('QQQ: subcomment.CommentCode[0:commentCodeEndPos]: %s' % subcomment.CommentCode[0:commentCodeEndPos])
            logging.info('QQQ: subcomment.CommentCode: %s' % subcomment.CommentCode)
            if subcomment.CommentCode[0:commentCodeEndPos] == Comment.CommentCode:
                logging.info('QQQ: in if subcomment.CommentCode[0:commentCodeEndPos] == subcomment.CommentCode')
                logging.info('QQQ: len(subcomment.CommentCode): %s' % len(subcomment.CommentCode))
                if len(subcomment.CommentCode) == (CommentCodeLen+1):
                    logging.info('QQQ: in if len(subcomment.CommentCode) == (CommentCodeLen+1)')
                    SubCommentCnt = SubCommentCnt + 1
                    logging.info('QQQ: SubCommentCnt: %s' % SubCommentCnt)
                    if subcomment.CommentCode[CommentCodeLen] > CommentCodeMax:
                        logging.info('QQQ: in if subcomment.CommentCode[CommentCodeLen] > CommentCodeMax')
                        CommentCodeMax = subcomment.CommentCode[CommentCodeLen]
                        logging.info('QQQ: CommentCodeMax: %s' % CommentCodeMax)

        logging.info('QQQ: SubCommentCnt: %d' % SubCommentCnt)

        logging.info('QQQ: CommentCodeMax: %s' % CommentCodeMax)
					
#                if comment.CommentCode > CommentMax:
#                    CommentMax = comment.CommentCode
#        if CommentMax == chr(ord('A') - 1):
#		    CommentMax = 'A'
#        if comments.CommentCode:
#            CommentCodeX = chr(ord(comments.CommentCode) + 1)
#        else:
#            CommentCodeX = 'A'

        if SubCommentCnt == 0:
            SubCommentCode = Comment.CommentCode + 'A'
        else:
            CommentCodeMax2 = chr(ord(CommentCodeMax) + 1)
            PartCommentCode = Comment.CommentCode[:CommentCodeLen]
            SubCommentCode = PartCommentCode + CommentCodeMax2

        RefObjID=self.request.get('RefObjID')
        CreatedBy = users.get_current_user()


#        if comments.CommentCode:
#            CommentCodeX = chr(ord(comments.CommentCode) + 1)
#        else:
#            CommentCodeX = 'A'

        n = Comments(Title=self.request.get('Title'),
                RefObjType=self.request.get('RefObjType'),
                RefObjID=RefObjID,
                CommentCode=SubCommentCode,
                Text=self.request.get('Text'),
#                Status=self.request.get('Status'),
                CreatedBy=CreatedBy#,
#                StatusBy=CreatedBy
                )

        logging.info('QQQ: CommentSub Create before put')
        n.put()
        logging.info('QQQ: CommentSub Create after put')

        x = self.redirect('/papers')
        logging.info('QQQ: CommentSub Create calc x')
        logging.info('QQQ: x: %s' % x)
        return x

    def get(self, comment_id):
        iden = int(comment_id)
        Comment = db.get(db.Key.from_path('Comments', iden))
        RefObjType = Comment.RefObjType
        RefObjID = Comment.RefObjID
        mgnwidth = 0
        #template_values = {
        #    'Comment': Comment,
        #    }
        StatusList = ['Pending Translation', 'Pending Review', 'Published'];
        CategoryList = ['Goals', 'Learning Resources', 'Learning Platform', 'Winning Students', 'Recruiting Volunteers'];

        jinja_environment = \
            jinja2.Environment(autoescape=False, loader=jinja2.FileSystemLoader(TEMPLATE_DIR))

        template_values = {
            'Comment': Comment, 
            'RefObjType': RefObjType,
            'RefObjID': RefObjID,
            'StatusList': StatusList,
            'CategoryList': CategoryList,
            'mgnwidth': mgnwidth
            }

        #TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'templates')
        jinja_environment = \
            jinja2.Environment(autoescape=False, loader=jinja2.FileSystemLoader(TEMPLATE_DIR))

        template = jinja_environment.get_template('CommentCreate.html')
        self.response.out.write(template.render(template_values))
			
#        self.render_template('CommentCreate.html', {'Comment': Comment, 'RefObjType': RefObjType, 'RefObjID': RefObjID, 'StatusList': StatusList, 'CategoryList': CategoryList})

class CommentDisplay(BaseHandler):

    def get(self, paper_id):
        iden = int(paper_id)
        Paper = db.get(db.Key.from_path('Papers', iden))
        template_values = {
            'Paper': Paper,
            'Title': Paper.Title,
            'content1': Paper.Text}

        #TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'templates')
        jinja_environment = \
            jinja2.Environment(autoescape=False, loader=jinja2.FileSystemLoader(TEMPLATE_DIR))

        template = jinja_environment.get_template('PaperDisplay.html')
        self.response.out.write(template.render(template_values))
		
		
		
        #StatusList = ['Pending Translation', 'Pending Review', 'Published'];
        #CategoryList = ['Goals', 'Learning Resources', 'Learning Platform', 'Winning Students', 'Recruiting Volunteers'];
        #self.render_template('PaperEdit.html', {'Paper': Paper, 'StatusList': StatusList, 'CategoryList': CategoryList})
        #self.render_template('PaperDisplay.html', {'Paper': Paper})

class CommentEdit(BaseHandler):

    def post(self, comment_id):
        iden = int(comment_id)
        Comment = db.get(db.Key.from_path('Comments', iden))
        currentuser = users.get_current_user()
        Comment.Title = self.request.get('Title')
        Comment.RefObjType = self.request.get('RefObjType')
        Comment.RefObjID = self.request.get('RefObjID')
        Comment.CommentCode = self.request.get('CommentCode')
        Comment.Text = self.request.get('Text')
        Comment.UpdatedBy = currentuser
        Comment.UpdatedDate = datetime.now()
        StatusPrev = Comment.Status
        Comment.Status = self.request.get('Status')
        if not Comment.Status == StatusPrev:
            Comment.StatusBy = currentuser
            Comment.StatusDate = datetime.now()            
        Comment.put()
        return self.redirect('/comments')

    def get(self, comment_id):
        iden = int(comment_id)
        Comment = db.get(db.Key.from_path('Comments', iden))
        StatusList = ['Pending Translation', 'Pending Review', 'Published'];
        CategoryList = ['Goals', 'Learning Resources', 'Learning Platform', 'Winning Students', 'Recruiting Volunteers'];
        self.render_template('CommentEdit.html', {'Comment': Comment, 'StatusList': StatusList, 'CategoryList': CategoryList})

class CommentDelete(BaseHandler):

    def get(self, paper_id):
        iden = int(paper_id)
        comment = db.get(db.Key.from_path('Comments', iden))
        db.delete(comment)
        return self.redirect('/comments')
