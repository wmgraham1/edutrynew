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

from models import TokenValues
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


class TokenStep1Page(BaseHandler):

    def get(self):
        #languages = Languages.all()
        languages = memcache.get("languages")
        if languages is not None:
           logging.info("get languages from memcache.")
        else:
           languages = Languages.query()
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

        langName = 'no language'
        for language in languages:
            if language.langCode == langCode:
                langName = language.langName

        PageCnt = self.session.get('PageCnt', 0)
        self.session['PageCnt'] = PageCnt + 1

        countmap_en={}
        langCode_en = 'en'
        q = TokenValues.query(TokenValues.langCode == langCode_en).order(TokenValues.langCode, TokenValues.tknID)
        tokens = q.fetch(99)
#        tokens = TokenValues.all().filter('langCode =', langCode_en)
        for token in tokens:
            logging.info('QQQ: token: %s' % token.langCode)
            if token.templateName in countmap_en:
                    countmap_en[token.templateName]=countmap_en[token.templateName]+1
            else:
                    countmap_en[token.templateName]=1

        countmap_other_language={}
        if langCode != 'en':    
            q = TokenValues.query(TokenValues.langCode == langCode).order(TokenValues.langCode, TokenValues.tknID)
            tokens = q.fetch(99)
#		tokens = TokenValues().all().filter('langCode =', langCode)
            for token in tokens:
                logging.info('QQQ: token: %s' % token.langCode)
                if token.templateName in countmap_other_language:
                        countmap_other_language[token.templateName]=countmap_other_language[token.templateName]+1
                else:
                        countmap_other_language[token.templateName]=1

        logout = None
        login = None
        currentuser = users.get_current_user()
        if currentuser:
              logout = users.create_logout_url('/tokens' )
        else:
              login = users.create_login_url('/tokens/create')

        self.render_template('TokenStep1.html', {'PageCnt':PageCnt, 'languages':languages, 'langCode':langCode, 'langName':langName, 'countmap_en':countmap_en, 'countmap_other_language':countmap_other_language, 'tokens': tokens,'currentuser':currentuser, 'login':login, 'logout': logout})

class TokenList(BaseHandler):

    def get(self):
        #langCode='en'
        langCode=self.request.get('langCode')

#        languages = Languages.all().filter('langCode =', langCode)
        q = Languages.query(Languages.langCode == langCode).order(Languages.langCode, Languages.langName)
        languages = q.fetch(99)

        langName = 'no language'
        for language in languages:
            if language.langCode == langCode:
                langName = language.langName

        templateName=self.request.get('templateName')

        q = TokenValues.query(TokenValues.langCode == langCode, TokenValues.templateName == templateName).order(TokenValues.langCode, TokenValues.templateName)
#        q = db.GqlQuery("SELECT * FROM TokenValues " + 
#                "WHERE langCode = :1 AND templateName = :2 " +
#                "ORDER BY tknID ASC",
#                langCode, templateName)
        tokens = q.fetch(999)

        logout = None
        login = None
        currentuser = users.get_current_user()
        if currentuser:
              logout = users.create_logout_url('/tokens' )
        else:
              login = users.create_login_url('/tokens/create')
        self.render_template('TokenList.html', {'tokens': tokens, 'langName':langName, 'templateName':templateName, 'currentuser':currentuser, 'login':login, 'logout': logout})

class TokenCreate(BaseHandler):

    def post(self):
        templateName = self.request.get('templateName')
        langCode = self.request.get('langCode')
        n = TokenValues(templateName=templateName,
                langCode=langCode,
                tknID=self.request.get('tknID'),
                tknValue=self.request.get('tknValue'), 
                whichuser=users.get_current_user()
                )

        n.put()
        #xyz = '/tokens?templateName=' + templateName + '&langCode=' + langCode
		#logging.info(xyz)
        #return webapp2.redirect('/tokens')
        return self.redirect('/tokens')

    def get(self):
        logout = None
        login = None
        currentuser = users.get_current_user()
        if currentuser:
              logout = users.create_logout_url('/tokens' )
        else:
              login = users.create_login_url('/tokens/create')
			  
        StatusList = ['Pending Translation', 'Pending Review', 'Published'];		  
        self.render_template('TokenCreate.html', {'StatusList': StatusList, 'currentuser':currentuser, 'login':login, 'logout': logout})


class TokenClone(BaseHandler):

    def get(self):
        languages = Languages.query()

        countmap_other_language={}
#		templateName2 = 'khan-exercise'	 and 'templateName', templateName2
        langCode2 = ''
        if self.request.get('langCode'):
            langCode2=self.request.get('langCode')
        if langCode2 == 'en':
            langCode2 = 'xx'
        if self.request.get('templateName'):
            templateName2=self.request.get('templateName')
        if langCode2 != 'en': 
            q = TokenValues.query(TokenValues.langCode == langCode2, TokenValues.templateName == templateName2).order(TokenValues.langCode2, TokenValues.templateName)
#		q = db.GqlQuery("SELECT * FROM TokenValues " + 
#                "WHERE langCode = :1 AND templateName = :2 " +
#                "ORDER BY tknID ASC",
#                langCode2, templateName2)
            tokens = q.fetch(999)		
#            tokens = TokenValues().all().filter('langCode =', langCode2)
            for token in tokens:
                logging.info('QQQ: token: %s' % token.langCode)
                if token.tknID not in countmap_other_language:
                        countmap_other_language[token.tknID]=1

        langCode='en'
        q = TokenValues.query(TokenValues.langCode == langCode, TokenValues.templateName == templateName).order(TokenValues.langCode2, TokenValues.templateName)
#        q = db.GqlQuery("SELECT * FROM TokenValues " + 
#            "WHERE langCode = :1 AND templateName = :2 " +
#            "ORDER BY tknID ASC",
#            langCode, templateName2)
        tokens = q.fetch(999)
#        tokens = TokenValues.all().filter('langCode =', langCode)

        logout = None
        login = None
        currentuser = users.get_current_user()
        if currentuser:
              logout = users.create_logout_url('/tokens' )
        else:
              login = users.create_login_url('/tokens/create')

        if langCode2 == 'xx':
            self.render_template('TokenStep1.html', {'languages':languages, 'langCode':langCode, 'countmap_other_language':countmap_other_language, 'tokens': tokens,'currentuser':currentuser, 'login':login, 'logout': logout})
        else:		
            for token in tokens:
                if token.tknID not in countmap_other_language:
                    n = TokenValues(templateName=token.templateName,
                        langCode=self.request.get('langCode'),
                        tknID=token.tknID,
                        tknValue=token.tknValue,
                        whichuser=users.get_current_user()
                        )
                    n.put()
            self.render_template('TokenStep1.html', {'languages':languages, 'langCode':langCode, 'countmap_other_language':countmap_other_language, 'tokens': tokens,'currentuser':currentuser, 'login':login, 'logout': logout})
		
		
class TokenEdit(BaseHandler):

    def post(self, token_id):
        iden = int(token_id)
        token = ndb.Key('TokenValues', iden).get()
#        token = db.get(db.Key.from_path('TokenValues', iden))
        currentuser = users.get_current_user()
        if currentuser != token.whichuser and not users.is_current_user_admin():
            self.abort(403)
            return
        token.templateName = self.request.get('templateName')
        token.langCode = self.request.get('langCode')
        token.tknID = self.request.get('tknID')
        token.tknValue = self.request.get('tknValue')
        token.date = datetime.now()
        token.put()
        return self.redirect('/tokens')

    def get(self, token_id):
        iden = int(token_id)
        token = ndb.Key('TokenValues', iden).get()
#        token = db.get(db.Key.from_path('TokenValues', iden))
        currentuser = users.get_current_user()
        if currentuser != token.whichuser and not users.is_current_user_admin():
            self.abort(403)
            return
        logout = None
        login = None
        currentuser = users.get_current_user()
        if currentuser:
              logout = users.create_logout_url('/tokens' )
        else:
              login = users.create_login_url('/tokens')
        self.render_template('TokenEdit.html', {'token': token,'currentuser':currentuser, 'login':login, 'logout': logout})


class TokenDelete(BaseHandler):

    def get(self, token_id):
        iden = int(token_id)
        token = ndb.Key('TokenValues', iden).get()
#        token = db.get(db.Key.from_path('TokenValues', iden))
        currentuser = users.get_current_user()
        if currentuser != token.whichuser and not users.is_current_user_admin():
            self.abort(403)
            return

#        db.delete(token)
        token.key.delete()

        return self.redirect('/tokens')
