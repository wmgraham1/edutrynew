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

class CommentList(BaseHandler):

    def get(self):

        q = Comments.query().order(Comments.RefObjType, Comments.RefObjID, Comments.CommentCode)
        comments = q.fetch(99)
		
        logout = None
        login = None
        currentuser = users.get_current_user()
        if currentuser:
              logout = users.create_logout_url('/comments' )
        else:
              login = users.create_login_url('/comments')
        self.render_template('CommentList.html', {'Comments': comments, 'currentuser':currentuser, 'login':login, 'logout': logout})


class CommentCreate(BaseHandler):

    def post(self, paper_id):
        logging.info('QQQ: Comment Create POST')

        RefObjID=self.request.get('RefObjID')
        CreatedBy = users.get_current_user()

        q = Comments.query(Comments.RefObjType == 'paper', Comments.RefObjID == paper_id).order(-Comments.CommentCode)
        comments = q.get()

        try:
            if comments.CommentCode:
                CommentCodeX = chr(ord(comments.CommentCode[0]) + 1)
            else:
                CommentCodeX = 'A'
        except AttributeError:
                CommentCodeX = 'A'

        n = Comments(Title=self.request.get('Title'),
                RefObjType=self.request.get('RefObjType'),
                RefObjID=RefObjID,
                CommentCode=CommentCodeX,
                IndentClass=len(CommentCodeX),
                Text=self.request.get('Text'),
                Status='Published',
                CreatedBy=CreatedBy,
                StatusBy=CreatedBy)
        n.put()

        x = self.redirect('/papers/display/' + paper_id)
        return x

    def get(self, paper_id):
        iden = int(paper_id)
        Paper = ndb.Key('Papers', iden).get()

        RefObjType = 'paper'
        RefObjID = paper_id
        mgnwidth = 0

        StatusList = ['Pending Translation', 'Pending Review', 'Published'];
        CategoryList = ['Goals', 'Learning Resources', 'Learning Platform', 'Winning Students', 'Recruiting Volunteers'];

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

class CommentSubCreate(BaseHandler):

    def post(self, comment_id):
        iden = int(comment_id)
        Comment = ndb.Key('Comments', iden).get()

        RefObjID=self.request.get('RefObjID')
        q = Comments.query(Comments.RefObjType == 'paper', Comments.RefObjID == RefObjID).order(-Comments.CommentCode)
        comments = q.fetch(99)

        CommentCodeLen = len(Comment.CommentCode)
        commentCodeEndPos = CommentCodeLen
        CommentCodeMax = chr(ord('A') - 1)
        SubCommentCnt = 0
        for subcomment in comments:
            if subcomment.CommentCode[0:commentCodeEndPos] == Comment.CommentCode:
                if len(subcomment.CommentCode) == (CommentCodeLen+1):
                    SubCommentCnt = SubCommentCnt + 1
                    if subcomment.CommentCode[CommentCodeLen] > CommentCodeMax:
                        CommentCodeMax = subcomment.CommentCode[CommentCodeLen]

        if SubCommentCnt == 0:
            SubCommentCode = Comment.CommentCode + 'A'
        else:
            CommentCodeMax2 = chr(ord(CommentCodeMax) + 1)
            PartCommentCode = Comment.CommentCode[:CommentCodeLen]
            SubCommentCode = PartCommentCode + CommentCodeMax2

        RefObjID=self.request.get('RefObjID')
        CreatedBy = users.get_current_user()

        n = Comments(Title=self.request.get('Title'),
                RefObjType=self.request.get('RefObjType'),
                RefObjID=RefObjID,
                CommentCode=SubCommentCode,
                IndentClass=len(SubCommentCode),
                Text=self.request.get('Text'),
                Status='Published',
                CreatedBy=CreatedBy,
                StatusBy=CreatedBy)
        n.put()

        return self.redirect('/papers/display/' + RefObjID)

    def get(self, comment_id):
        iden = int(comment_id)
        Comment = ndb.Key('Comments', iden).get()

        RefObjType = Comment.RefObjType
        RefObjID = Comment.RefObjID
        mgnwidth = 0

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

class CommentEdit(BaseHandler):

    def post(self, comment_id):
        iden = int(comment_id)
        Comment = ndb.Key('Comments', iden).get()
        currentuser = users.get_current_user()
        Comment.Title = self.request.get('Title')
        Comment.RefObjType = self.request.get('RefObjType')
        Comment.RefObjID = self.request.get('RefObjID')
        Comment.CommentCode = self.request.get('CommentCode')
        Comment.IndentClass=len(self.request.get('CommentCode'))
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
        Comment = ndb.Key('Comments', iden).get()
        StatusList = ['Pending Translation', 'Pending Review', 'Published'];
        CategoryList = ['Goals', 'Learning Resources', 'Learning Platform', 'Winning Students', 'Recruiting Volunteers'];
        self.render_template('CommentEdit.html', {'Comment': Comment, 'StatusList': StatusList, 'CategoryList': CategoryList})

class CommentDelete(BaseHandler):

    def get(self, paper_id):
        iden = int(paper_id)
        Comment = ndb.Key('Comments', iden).get()
        Comment.key.delete()
        return self.redirect('/comments')
