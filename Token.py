from __future__ import with_statement
import jinja2
import os
import webapp2
import logging
from datetime import datetime
from google.appengine.ext import db
from google.appengine.ext import ndb
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.api import users
from webapp2_extras import sessions
from google.appengine.api import memcache
from SecurityUtils import AccessOK
from google.appengine.api import files

from models import TokenValues
from models import Languages
from models import Templates
from models import GeneratedFiles


TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'templates')
jinja_environment = \
    jinja2.Environment(autoescape=False, loader=jinja2.FileSystemLoader(TEMPLATE_DIR))
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


class TokenStep1PageEx(BaseHandler):

    def get(self):
        #languages = Languages.all()
        languages = memcache.get("languages")
        if languages is not None:
            logging.info("get languages from memcache.")
        else:
            q = Languages.query().order(Languages.langName)
            languages = q.fetch(99)
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
        tokens = q.fetch(999)
#        tokens = TokenValues.all().filter('langCode =', langCode_en)
        for token in tokens:
#            logging.info('QQQ: token_en: %s' % token.langCode)
            if token.templateName in countmap_en:
                    countmap_en[token.templateName]=countmap_en[token.templateName]+1
            else:
                    countmap_en[token.templateName]=1

        countmap_other_language={}
        if langCode != 'en':    
            q = TokenValues.query(TokenValues.langCode == langCode).order(TokenValues.langCode, TokenValues.tknID)
            tokens = q.fetch(999)
#		tokens = TokenValues().all().filter('langCode =', langCode)
            for token in tokens:
#                logging.info('QQQ: token_non-EN: %s' % token.langCode)
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
              login = users.create_login_url('/tokens')

        self.render_template('TokenStep1.html', {'PageCnt':PageCnt, 'languages':languages, 'langCode':langCode, 'langName':langName, 'countmap_en':countmap_en, 'countmap_other_language':countmap_other_language, 'tokens': tokens,'currentuser':currentuser, 'login':login, 'logout': logout})

class TokenStep1Page(BaseHandler):

    def get(self):
        #languages = Languages.all()
        languages = memcache.get("languages")
        if languages is not None:
            logging.info("get languages from memcache.")
        else:
            q = Languages.query().order(Languages.langName)
            languages = q.fetch(99)
            logging.info("Can not get languages from memcache.")
            if not memcache.add("languages", languages, 10):
                logging.info("Memcache set failed.")

        if self.request.get('extyp'):
            extyp=self.request.get('extyp')
            self.session['extyp'] = extyp
        else:
            extyp = self.session.get('extyp')
        if not extyp:
            self.session['extyp'] = 'exercise'

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
        tokens = q.fetch(999)
#        tokens = TokenValues.all().filter('langCode =', langCode_en)
        for token in tokens:
#            logging.info('QQQ: token_en: %s' % token.langCode)
            if token.templateName in countmap_en:
                    countmap_en[token.templateName]=countmap_en[token.templateName]+1
            else:
                    countmap_en[token.templateName]=1

        countmap_other_language={}
        if langCode != 'en':    
            q = TokenValues.query(TokenValues.langCode == langCode).order(TokenValues.langCode, TokenValues.tknID)
            tokens = q.fetch(999)
#		tokens = TokenValues().all().filter('langCode =', langCode)
            for token in tokens:
#                logging.info('QQQ: token_non-EN: %s' % token.langCode)
                if token.templateName in countmap_other_language:
                        countmap_other_language[token.templateName]=countmap_other_language[token.templateName]+1
                else:
                        countmap_other_language[token.templateName]=1

        ExerciseList=[]
        q = Templates.query(Templates.TemplateType != 'exercise')
        templates = q.fetch(99)
        
        for template in templates:
            logging.info('QQQ: TokenListStep1Page: %s' % template.Name)
            ExerciseList.append(template.Name)

        logout = None
        login = None
        currentuser = users.get_current_user()
        if currentuser:
              logout = users.create_logout_url('/tokens' )
        else:
              login = users.create_login_url('/tokens')

        self.render_template('TokenStep1.html', {'PageCnt':PageCnt, 'extyp':extyp, 'languages':languages, 'langCode':langCode, 'langName':langName, 'countmap_en':countmap_en, 'countmap_other_language':countmap_other_language, 'ExerciseList': ExerciseList, 'tokens': tokens,'currentuser':currentuser, 'login':login, 'logout': logout})

class TokenList(BaseHandler):

    def get(self):
        #langCode='en'

        if self.request.get('langCode'):
            langCode=self.request.get('langCode')
            self.session['langCode'] = langCode
        else:
            langCode = self.session.get('langCode')

        if self.request.get('templateName'):
            templateName=self.request.get('templateName')
            self.session['templateName'] = templateName
        else:
            templateName = self.session.get('templateName')

        if self.request.get('extyp'):
            extyp=self.request.get('extyp')
            self.session['extyp'] = extyp
        else:
            extyp = self.session.get('extyp')
        if not extyp:
            self.session['extyp'] = 'exercise'

        if self.request.get('StatusFilter'):
            StatusFilter=self.request.get('StatusFilter')
            self.session['StatusFilter'] = StatusFilter
        else:
            StatusFilter = self.session.get('StatusFilter')
        if not StatusFilter:
            self.session['StatusFilter'] = 'all'
            StatusFilter = 'all'

        if self.request.get('TopGrpFilter'):
            TopGrpFilter=self.request.get('TopGrpFilter')
            self.session['TopGrpFilter'] = TopGrpFilter
        else:
            TopGrpFilter = self.session.get('TopGrpFilter')
        if not TopGrpFilter:
            self.session['TopGrpFilter'] = 'all'
            TopGrpFilter = 'all'

        countmap_en=0
        langCode_en = 'en'
        q = TokenValues.query(TokenValues.langCode == langCode_en, TokenValues.templateName == templateName).order(TokenValues.langCode, TokenValues.tknID)
        tokens = q.fetch(999, keys_only=True)
#        tokens = TokenValues.all().filter('langCode =', langCode_en)
        for token in tokens:
#            logging.info('QQQ: token_en: %s' % token.langCode)
            countmap_en=countmap_en+1

        countmap_other_language=0
        if langCode != 'en':    
            q = TokenValues.query(TokenValues.langCode == langCode, TokenValues.templateName == templateName).order(TokenValues.langCode, TokenValues.tknID)
            tokens = q.fetch(999, keys_only=True)
#		tokens = TokenValues().all().filter('langCode =', langCode)
            for token in tokens:
#                logging.info('QQQ: token_non-EN: %s' % token.langCode)
                countmap_other_language=countmap_other_language+1

#        languages = Languages.all().filter('langCode =', langCode)
        q = Languages.query().order(Languages.langName)
        languages = q.fetch(999)

        langName = 'no language'
        for language in languages:
            if language.langCode == langCode:
                langName = language.langName

        q = TokenValues.query(TokenValues.langCode == langCode, TokenValues.templateName == templateName, TokenValues.Status != 'Published')
        TokensNotReady = q.get()

        if TokensNotReady:
            TemplateGenReady = False
        else:        
            TemplateGenReady = True
        
        q = GeneratedFiles.query(GeneratedFiles.LangCode == langCode, GeneratedFiles.TemplateName == templateName).order(-GeneratedFiles.CreatedDate)
        GenFile = q.get()

        TryReady = False
        if GenFile:
            GenFileReady = GenFile.key.id()
            SearchName = GenFile.SearchName
            q2 = Templates.query(Templates.Name == GenFile.TemplateName)
            GenFileTemplate = q2.get()
            if GenFileTemplate.TemplateType == 'exercise':
                TryReady = True
            else:
                TryReady = False
        else:        
            GenFileReady = None
            SearchName = None
            TryReady = False
        logging.info('GGG: Token.py/TryReady: %s' % TryReady)

        logging.info('GGG: StatusFilter in TokenList: %s' % StatusFilter)
        if StatusFilter == 'all':
            q = TokenValues.query(TokenValues.langCode == langCode, TokenValues.templateName == templateName).order(TokenValues.langCode, TokenValues.templateName, TokenValues.tknID)
        else:
            q = TokenValues.query(TokenValues.langCode == langCode, TokenValues.templateName == templateName, TokenValues.Status == StatusFilter).order(TokenValues.langCode, TokenValues.templateName, TokenValues.tknID)
        tokens = q.fetch(999)

        logout = None
        login = None
        currentuser = users.get_current_user()
        if currentuser:
              logout = users.create_logout_url('/tokens' )
        else:
              login = users.create_login_url('/tokens')

        StatusList = ['Pending Translation', 'Pending Review', 'Published'];

        self.render_template('TokenList.html', {'tokens': tokens, 'langName':langName, 'extyp':extyp, 'count_en':countmap_en, 'count_other_language':countmap_other_language, 'StatusList':StatusList, 'StatusFilter':StatusFilter, 'TopGrpFilter':TopGrpFilter, 'templateName':templateName, 'languages':languages, 'langCode':langCode, 'SearchName':SearchName, 'GenFileReady':GenFileReady, 'TryReady':TryReady, 'TemplateGenReady':TemplateGenReady, 'currentuser':currentuser, 'login':login, 'logout': logout})

class TokenEditList(BaseHandler):

    def get(self):
        #langCode='en'

        if self.request.get('langCode'):
            langCode=self.request.get('langCode')
            self.session['langCode'] = langCode
        else:
            langCode = self.session.get('langCode')

        if self.request.get('templateName'):
            templateName=self.request.get('templateName')
            self.session['templateName'] = templateName
        else:
            templateName = self.session.get('templateName')

        if self.request.get('extyp'):
            extyp=self.request.get('extyp')
            self.session['extyp'] = extyp
        else:
            extyp = self.session.get('extyp')
        if not extyp:
            self.session['extyp'] = 'exercise'

        if self.request.get('StatusFilter'):
            StatusFilter=self.request.get('StatusFilter')
            self.session['StatusFilter'] = StatusFilter
        else:
            StatusFilter = self.session.get('StatusFilter')
        if not StatusFilter:
            self.session['StatusFilter'] = 'all'
            StatusFilter = 'all'

        if self.request.get('TopGrpFilter'):
            TopGrpFilter=self.request.get('TopGrpFilter')
            self.session['TopGrpFilter'] = TopGrpFilter
        else:
            TopGrpFilter = self.session.get('TopGrpFilter')
        if not TopGrpFilter:
            self.session['TopGrpFilter'] = 'all'
            TopGrpFilter = 'all'

        countmap_en=0
        langCode_en = 'en'
        q = TokenValues.query(TokenValues.langCode == langCode_en, TokenValues.templateName == templateName).order(TokenValues.langCode, TokenValues.tknID)
        tokens = q.fetch(999, keys_only=True)
#        tokens = TokenValues.all().filter('langCode =', langCode_en)
        for token in tokens:
#            logging.info('QQQ: token_en: %s' % token.langCode)
            countmap_en=countmap_en+1

        countmap_other_language=0
        if langCode != 'en':    
            q = TokenValues.query(TokenValues.langCode == langCode, TokenValues.templateName == templateName).order(TokenValues.langCode, TokenValues.tknID)
            tokens = q.fetch(999, keys_only=True)
#		tokens = TokenValues().all().filter('langCode =', langCode)
            for token in tokens:
#                logging.info('QQQ: token_non-EN: %s' % token.langCode)
                countmap_other_language=countmap_other_language+1

#        languages = Languages.all().filter('langCode =', langCode)
        q = Languages.query().order(Languages.langName)
        languages = q.fetch(999)

        langName = 'no language'
        for language in languages:
            if language.langCode == langCode:
                langName = language.langName

        q = TokenValues.query(TokenValues.langCode == langCode, TokenValues.templateName == templateName, TokenValues.Status != 'Published')
        TokensNotReady = q.get()

        if TokensNotReady:
            TemplateGenReady = False
        else:        
            TemplateGenReady = True
        
        q = GeneratedFiles.query(GeneratedFiles.LangCode == langCode, GeneratedFiles.TemplateName == templateName).order(-GeneratedFiles.CreatedDate)
        GenFile = q.get()

        if GenFile:
            GenFileReady = GenFile.key.id()
            SearchName = GenFile.SearchName
        else:        
            GenFileReady = None
            SearchName = None

        logging.info('GGG: StatusFilter in TokenList: %s' % StatusFilter)
        if StatusFilter == 'all':
            q = TokenValues.query(TokenValues.langCode == langCode, TokenValues.templateName == templateName).order(TokenValues.langCode, TokenValues.templateName, TokenValues.tknID)
        else:
            q = TokenValues.query(TokenValues.langCode == langCode, TokenValues.templateName == templateName, TokenValues.Status == StatusFilter).order(TokenValues.langCode, TokenValues.templateName, TokenValues.tknID)
        tokens = q.fetch(999)

        if StatusFilter == 'all':
            f = TokenValues.query(TokenValues.langCode == 'en', TokenValues.templateName == templateName)
        else:
            f = TokenValues.query(Subjects.LangCode == 'en', TokenValues.templateName == templateName, TokenValues.Status == StatusFilter)

        units_en = f.fetch(999)
        
        dict_units_en = {}
        dict_units_en['DummyTemplate'] = 'no content'
        dict_Context_en = {}
        dict_Context_en['DummyTemplate'] = 'no content'
        for unit_en in units_en:
#            logging.info('GGG: Subjects.py/LearningUnitID: %s' % unit_en.LearningUnitID)
#            logging.info('GGG: Subjects.py/Description: %s' % unit_en.Description)
#            if unit_en.Context:
#                dict_units_en[unit_en.tknID] = unit_en.tknValue + ' in (' + unit_en.Context + ')'
#            else:
#                dict_units_en[unit_en.tknID] = unit_en.tknValue
            dict_units_en[unit_en.tknID] = unit_en.tknValue
            dict_Context_en[unit_en.tknID] = unit_en.Context

        TryReady = False
        if GenFile:
            GenFileReady = GenFile.key.id()
            SearchName = GenFile.SearchName
            q2 = Templates.query(Templates.Name == GenFile.TemplateName)
            GenFileTemplate = q2.get()
            if GenFileTemplate.TemplateType == 'exercise':
                TryReady = True
            else:
                TryReady = False
        else:        
            GenFileReady = None
            SearchName = None
            TryReady = False
        logging.info('GGG: Token.py/TryReady: %s' % TryReady)

        logout = None
        login = None
        currentuser = users.get_current_user()
        if currentuser:
              logout = users.create_logout_url('/tokens' )
        else:
              login = users.create_login_url('/tokens')

        StatusList = ['Pending Translation', 'Pending Review', 'Published'];

        self.render_template('TokenListEdit.html', {'tokens': tokens, 'langName':langName, 'extyp':extyp, 'count_en':countmap_en, 'count_other_language':countmap_other_language, 'StatusList':StatusList, 'StatusFilter':StatusFilter, 'TopGrpFilter':TopGrpFilter, 'templateName':templateName, 'dict_units_en':dict_units_en, 'dict_Context_en':dict_Context_en, 'languages':languages, 'langCode':langCode, 'SearchName':SearchName, 'TryReady':TryReady, 'GenFileReady':GenFileReady, 'TemplateGenReady':TemplateGenReady, 'currentuser':currentuser, 'login':login, 'logout': logout})

class TokenCreate(BaseHandler):

    def post(self):
        templateName = self.request.get('templateName')
        langCode = self.request.get('langCode')
        tknID = self.request.get('tknID')

        q = TokenValues.query(TokenValues.langCode == langCode, TokenValues.templateName == templateName, TokenValues.tknID == tknID).order(TokenValues.langCode, TokenValues.templateName, TokenValues.tknID)
        tokens = q.get()
        if tokens:
            logging.info('QQQ: In CreateToken Returning as DuptknID=: %s' % tknID)
            return self.redirect('/tokens/create?templateName=' + templateName + '&langCode=' + langCode + '&msg=dup' + '&tknID=' + tknID)
        else:
            logging.info('QQQ: In CreateToken putting content tknID=: %s' % tknID)
            n = TokenValues(templateName = templateName
                    , langCode = langCode
                    , tknID = tknID
                    , tknValue = self.request.get('tknValue')
                    , Context = self.request.get('Context')
                    , Status = 'Pending Translation'
                    )
            n.put()
            #xyz = '/tokens?templateName=' + templateName + '&langCode=' + langCode
            #logging.info(xyz)
            #return webapp2.redirect('/tokens')
            return self.redirect('/tokens?templateName=' + templateName + '&langCode=' + langCode)
		
		
    def get(self):
        Dup = False
        if self.request.get('msg') == 'dup':
            Dup = True

        tknID = self.request.get('tknID')
        
        templateName = self.request.get('tName')
        languages = memcache.get("languages")
        if languages is not None:
            logging.info("get languages from memcache.")
        else:
            q = Languages.query().order(Languages.langName)
            languages = q.fetch(99)
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

        q = Languages.query().order(Languages.langCode, Languages.langName)
        languages = q.fetch(999)

        langName = 'no language'
        for language in languages:
            if language.langCode == langCode:
                langName = language.langName

        if self.request.get('extyp'):
            extyp=self.request.get('extyp')
            self.session['extyp'] = extyp
        else:
            extyp = self.session.get('extyp')
        if not extyp:
            self.session['extyp'] = 'exercise'

#        templates = Templates.query()
        q = Templates.query().order(Templates.Name)
        templates = q.fetch(99)
				
        logout = None
        login = None
        currentuser = users.get_current_user()
        if currentuser:
              logout = users.create_logout_url('/tokens' )
        else:
              login = users.create_login_url('/tokens/create')
        Src = 'top'	  
        StatusList = ['Pending Translation', 'Pending Review', 'Published'];		  
        self.render_template('TokenCreate.html', {'templates': templates, 'Src': Src, 'extyp':extyp, 'templateName': templateName, 'Dup': Dup, 'tknID': tknID, 'StatusList': StatusList, 'languages':languages, 'langCode':langCode, 'langName':langName, 'currentuser':currentuser, 'login':login, 'logout': logout})

class TemplateTokenCreate(BaseHandler):

    def post(self):
        templateName = self.request.get('templateName')
        langCode = self.request.get('langCode')
        tknID = self.request.get('tknID')

        if self.request.get('extyp'):
            extyp=self.request.get('extyp')
            self.session['extyp'] = extyp
        else:
            extyp = self.session.get('extyp')
        if not extyp:
            self.session['extyp'] = 'exercise'

        q = TokenValues.query(TokenValues.langCode == langCode, TokenValues.templateName == templateName, TokenValues.tknID == tknID).order(TokenValues.langCode, TokenValues.templateName, TokenValues.tknID)
        tokens = q.get()
        if tokens:
            logging.info('QQQ: In CreateToken Returning as DuptknID=: %s' % tknID)
            return self.redirect('/tokens/createt?tName=' + templateName + '&langCode=' + langCode + '&msg=dup' + '&tknID=' + tknID)
        else:
            logging.info('QQQ: In CreateToken putting content tknID=: %s' % tknID)
            n = TokenValues(templateName=templateName
                    , langCode=langCode
                    , tknID = tknID
                    , tknValue=self.request.get('tknValue')
                    , Context = self.request.get('Context')
                    , Status = 'Pending Translation'
                    )
            n.put()
            return self.redirect('/tokens?templateName=' + templateName + '&langCode=' + langCode)
		
		
    def get(self):
        Dup = False
        if self.request.get('msg') == 'dup':
            Dup = True
        tknID = self.request.get('tknID')
        templateName = self.request.get('tName')

        languages = memcache.get("languages")
        if languages is not None:
            logging.info("get languages from memcache.")
        else:
            q = Languages.query().order(Languages.langName)
            languages = q.fetch(99)
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

        q = Languages.query().order(Languages.langCode, Languages.langName)
        languages = q.fetch(999)

        langName = 'no language'
        for language in languages:
            if language.langCode == langCode:
                langName = language.langName

        q = Templates.query().order(Templates.Name)
        templates = q.fetch(99)

        if self.request.get('extyp'):
            extyp=self.request.get('extyp')
            self.session['extyp'] = extyp
        else:
            extyp = self.session.get('extyp')
        if not extyp:
            self.session['extyp'] = 'exercise'

        logout = None
        login = None
        currentuser = users.get_current_user()
        if currentuser:
              logout = users.create_logout_url('/tokens' )
        else:
              login = users.create_login_url('/tokens/create')
        Src = 'template'	  
        StatusList = ['Pending Translation', 'Pending Review', 'Published'];		  
        self.render_template('TokenCreate.html', {'templates': templates, 'Src': Src, 'extyp':extyp, 'templateName': templateName, 'Dup': Dup, 'tknID': tknID, 'StatusList': StatusList, 'languages':languages, 'langCode':langCode, 'langName':langName, 'currentuser':currentuser, 'login':login, 'logout': logout})

class TokenEditListPost(BaseHandler):

    def post(self, token_id):
        iden = int(token_id)
        logging.info('GGG: in TokenEditListPost/iden: %s' % iden)
        token = ndb.Key('TokenValues', iden).get()
        currentuser = users.get_current_user()
#        if currentuser != token.whichuser and not users.is_current_user_admin():
#            self.abort(403)
#            return
#        templateName = self.request.get('templateName')
#        langCode = self.request.get('langCode')
#        token.templateName = templateName
#        token.langCode = langCode
#        token.tknID = self.request.get('tknID')
        token.tknID = self.request.get('tknID')
        logging.info('GGG: in TokenEditListPost/old TokenVal: %s' % token.tknValue)
        token.tknValue = self.request.get('tknValue')
        logging.info('GGG: in TokenEditListPost/new TokenVal: %s' % token.tknValue)
        StatusPrev = token.Status
        token.Status = self.request.get('Status')
        logging.info('GGG: in TokenEditListPost/token.Status: %s' % token.Status)
        if not token.Status == StatusPrev:
            token.StatusBy = currentuser
            token.StatusDate = datetime.now()    
        token.UpdatedBy = currentuser
        token.UpdatedDate = datetime.now()    
        token.put()
#        return self.redirect('/tokens?templateName=' + templateName + '&langCode=' + langCode)
		
class TokenEdit(BaseHandler):

    def post(self, token_id):
        iden = int(token_id)
        token = ndb.Key('TokenValues', iden).get()
        currentuser = users.get_current_user()
#        if currentuser != token.whichuser and not users.is_current_user_admin():
#            self.abort(403)
#            return
        templateName = self.request.get('templateName')
        langCode = self.request.get('langCode')
        token.templateName = templateName
        token.langCode = langCode
        token.tknID = self.request.get('tknID')
        token.tknValue = self.request.get('tknValue')
        token.tknValue2 = self.request.get('tknValue')
        token.Context = self.request.get('Context')
        StatusPrev = token.Status
        token.Status = self.request.get('Status')
        if not token.Status == StatusPrev:
            token.StatusBy = currentuser
            token.StatusDate = datetime.now()    
        token.put()
        return self.redirect('/tokens?templateName=' + templateName + '&langCode=' + langCode)

    def get(self, token_id):
        iden = int(token_id)
        token = ndb.Key('TokenValues', iden).get()
        logging.info('GGG: token.langCode: %s' % token.langCode)
        tknValue_en = 'no entry'
        Context_en = 'no entry'
        if  (token.langCode != 'en'):
            TemplateName_en = token.templateName
            tknID_en = token.tknID
            logging.info('GGG: TemplateName_en: %s' % TemplateName_en)
            logging.info('GGG: tknID_en: %s' % tknID_en)
            logging.info('GGG: tknValue: %s' % token.tknValue)
            q = TokenValues.query(TokenValues.templateName == TemplateName_en, TokenValues.tknID == tknID_en, TokenValues.langCode == 'en')
            TokenVal_en = q.get()
            logging.info('GGG: TokenVal_en.templateName: %s' % TokenVal_en.templateName)
            logging.info('GGG: TokenVal_en.tknID: %s' % TokenVal_en.tknID)
            logging.info('GGG: TokenVal_en.langCode: %s' % TokenVal_en.langCode)
            logging.info('GGG: TokenVal_en.tknValue: %s' % TokenVal_en.tknValue)
            logging.info('GGG: TemplateName_en: %s' % TemplateName_en)
            logging.info('GGG: tknID_en: %s' % tknID_en)
            logging.info('GGG: tknValue: %s' % token.tknValue)
            tknValue_en = TokenVal_en.tknValue
            Context_en = TokenVal_en.Context

#        token = db.get(db.Key.from_path('TokenValues', iden))
        currentuser = users.get_current_user()
#        if currentuser != token.whichuser and not users.is_current_user_admin():
#            self.abort(403)
#            return
        logout = None
        login = None
        currentuser = users.get_current_user()
        if currentuser:
              logout = users.create_logout_url('/tokens' )
        else:
              login = users.create_login_url('/tokens')
        StatusList = ['Pending Translation', 'Pending Review', 'Published'];
        TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'templates')
        jinja_environment = \
            jinja2.Environment(autoescape=True, loader=jinja2.FileSystemLoader(TEMPLATE_DIR))
        self.render_template('TokenEdit.html', {'token': token, 'tknValue_en': tknValue_en, 'Context_en': Context_en, 'StatusList': StatusList, 'currentuser':currentuser, 'login':login, 'logout': logout})


class TokenDelete(BaseHandler):

    def get(self, token_id):
        iden = int(token_id)
        token = ndb.Key('TokenValues', iden).get()
        templateName = token.templateName
        langCode = token.langCode
#        token = db.get(db.Key.from_path('TokenValues', iden))
        currentuser = users.get_current_user()
#        if currentuser != token.whichuser and not users.is_current_user_admin():
#            self.abort(403)
#            return

#        db.delete(token)
        token.key.delete()
        return self.redirect('/tokens?templateName=' + templateName + '&langCode=' + langCode)

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
        else:
            templateName2='none'
        if langCode2 != 'en': 
            logging.info('GGG: langCode_just_B4_Query1_NotEN: %s' % langCode2)
            logging.info('GGG: templateName_just_B4_Query1_NotEN: %s' % templateName2)
            q = TokenValues.query(TokenValues.langCode == langCode2, TokenValues.templateName == templateName2).order(TokenValues.langCode, TokenValues.templateName)
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
        logging.info('GGG: langCode_just_B4_Query2_EN: %s' % langCode)
        logging.info('GGG: templateName_just_B4_Query2_EN: %s' % templateName2)
        q = TokenValues.query(TokenValues.langCode == langCode, TokenValues.templateName == templateName2).order(TokenValues.langCode, TokenValues.templateName)
#        q = db.GqlQuery("SELECT * FROM TokenValues " + 
#            "WHERE langCode = :1 AND templateName = :2 " +
#            "ORDER BY tknID ASC",
#            langCode, templateName2)
        tokens = q.fetch(999)
#        tokens = TokenValues.all().filter('langCode =', langCode)

        if self.request.get('extyp'):
            extyp=self.request.get('extyp')
            self.session['extyp'] = extyp
        else:
            extyp = self.session.get('extyp')
        if not extyp:
            self.session['extyp'] = 'exercise'

        logout = None
        login = None
        currentuser = users.get_current_user()
        if currentuser:
              logout = users.create_logout_url('/tokens' )
        else:
              login = users.create_login_url('/tokens/create')

        if langCode2 == 'xx':
            if extyp == 'exercise':
                return self.redirect('/tokens')
            else:
                return self.redirect('/tokens-step1')

#        self.render_template('TokenStep1.html', {'languages':languages, 'langCode':langCode, 'countmap_other_language':countmap_other_language, 'tokens': tokens,'currentuser':currentuser, 'login':login, 'logout': logout})
        else:		
            for token in tokens:
                if token.tknID not in countmap_other_language:
                    n = TokenValues(templateName=token.templateName
                        , langCode=self.request.get('langCode')
                        , tknID=token.tknID
                        , tknValue=token.tknValue
                        , tknValue2=token.tknValue2
                        )
                    n.put()
            if extyp == 'exercise':
                return self.redirect('/tokens')
            else:
                return self.redirect('/tokens-step1')
#            return self.redirect('/tokens?templateName=' + templateName2 + '&langCode=' + langCode)
#            self.render_template('TokenStep1.html', {'languages':languages, 'langCode':langCode, 'countmap_other_language':countmap_other_language, 'tokens': tokens,'currentuser':currentuser, 'login':login, 'logout': logout})
		
class TokenFileGen(BaseHandler):

    def get(self):

        templateName=self.request.get('templateName')
        langCode=self.request.get('langCode')

        if self.request.get('extyp'):
            extyp=self.request.get('extyp')
            self.session['extyp'] = extyp
        else:
            extyp = self.session.get('extyp')
        if not extyp:
            self.session['extyp'] = 'exercise'

        q = Templates.query(Templates.Name == templateName)
        template = q.get()
#        template = ndb.Key('Templates', iden).get()
        FolderName = template.FolderName
        FileName = template.FileName
        logging.info('RRR: template.TemplateType: %s' % template.TemplateType)
        logging.info('RRR: template.Name: %s' % template.Name)
        logging.info('RRR: template.FileName: %s' % template.FileName)
        logging.info('RRR: template.FolderName: %s' % template.FolderName)
        
        SearchName = ''
        if template.TemplateType == 'exercise':
            logging.info('RRR: INSIDE IF - template.TemplateType: %s' % template.TemplateType)
            SearchName = FileName
        elif template.TemplateType == 'none':
            logging.info('RRR: INSIDE IF / elif - template.TemplateType: %s' % template.TemplateType)
            SearchName = FileName
        else:
            logging.info('RRR: INSIDE FAILED IF - template.TemplateType: %s' % template.TemplateType)
            SearchName = template.FolderName + '/' + template.FileName
        logging.info('RRR: template.SearchName: %s' % SearchName)

        q = TokenValues.query(TokenValues.langCode == langCode, TokenValues.templateName == templateName).order(TokenValues.langCode, TokenValues.templateName, TokenValues.tknID)
        tokenvals = q.fetch(999)
        tokendict = {}
        for tokenval in tokenvals:
            tokendict[tokenval.tknID] = tokenval.tknValue
            logging.info('QQQ: TknID: %s' % tokenval.tknID)
            logging.info('QQQ: tknValue: %s' % tokenval.tknValue)
        #tokenvals = tokendict()

        currentuser = users.get_current_user()

        q = GeneratedFiles.query(GeneratedFiles.LangCode == langCode, GeneratedFiles.TemplateName == templateName)
        genfiles = q.fetch(9)
        if genfiles:
            for genfile in genfiles:
                genfile.key.delete()

        TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'tokenizedtemplates')
        jinja_environment = \
            jinja2.Environment(autoescape=False, loader=jinja2.FileSystemLoader(TEMPLATE_DIR))
        logging.info('QQQ: FileName: %s' % FileName)
        template = jinja_environment.get_template(FileName)
#        self.response.out.write(template.render(tokenvals = tokendict)) 
        
        blobtext = template.render(tokenvals = tokendict)
        bloboutput = (blobtext.encode('utf-8'))
        
        # Create the file
        file_name = files.blobstore.create(mime_type='application/octet-stream')
        # Open the file and write to it
        with files.open(file_name, 'a') as fl:
            fl.write(blobtext)
        # Finalize the file. Do this before attempting to read it.
        files.finalize(file_name)
        # Get the file's blob key
        blob_key = files.blobstore.get_blob_key(file_name)
        logging.info('QQQ: blob_key: %s' % blob_key)

        f = GeneratedFiles(
            TemplateName = templateName
            , FolderName = FolderName
            , SearchName = SearchName
            , LangCode = langCode
            , FileTxt = bloboutput
            , FileTxt2 = bloboutput
            , Status = 'Published'
            , blob = blob_key                       
            )
        f.put()
        TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'templates')
        jinja_environment = \
            jinja2.Environment(autoescape=False, loader=jinja2.FileSystemLoader(TEMPLATE_DIR))
        return self.redirect('/tokens?templateName=' + templateName + '&langCode=' + langCode)

class TokenFileView(BaseHandler):

    def get(self):
        iden = int(token_id)
        return self.redirect('/tokens?templateName=' + templateName + '&langCode=' + langCode)

