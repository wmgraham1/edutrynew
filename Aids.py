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


from models import LearnAids
from models import Languages

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

class LearnAidList(BaseHandler):

    def get(self):
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
            langCode = 'en'

        langName = 'no language'
        for language in languages:
            if language.langCode == langCode:
                langName = language.langName

        if self.request.get('StatusFilter'):
            StatusFilter=self.request.get('StatusFilter')
            self.session['StatusFilter'] = StatusFilter
        else:
            StatusFilter = self.session.get('StatusFilter')
        if not StatusFilter:
            self.session['StatusFilter'] = 'all'
            StatusFilter = 'all'

        count_en = 0
        langCode_en = 'en'
        q = LearnAids.query(LearnAids.LangCode == langCode_en)
        aids = q.fetch(999)
        for aid in aids:
            logging.info('QQQ: count_en: %d' % count_en)
            count_en = count_en + 1
        logging.info('QQQ: Total count_en: %d' % count_en)

        logging.info('QQQ: langCode: %s' % langCode)
        count_other_language = 0
        q2 = LearnAids.query(LearnAids.LangCode == langCode)
        aidsx = q2.fetch(999)
        for aid in aidsx:
            logging.info('QQQ: count_other_language: %d' % count_other_language)
            count_other_language = count_other_language + 1
        logging.info('QQQ: Total count_other_language: %d' % count_other_language)

        logging.info('GGG: StatusFilter in LearnAidList: %s' % StatusFilter)
        if StatusFilter == 'all':
            q = LearnAids.query(LearnAids.LangCode == langCode).order(LearnAids.LearnAidID)
        else:
            q = LearnAids.query(LearnAids.LangCode == langCode, LearnAids.Status == StatusFilter).order(LearnAids.LearnAidID)
        aids = q.fetch(999)

        logout = None
        login = None
        currentuser = users.get_current_user()
        if currentuser:
              logout = users.create_logout_url('/aids' )
        else:
              login = users.create_login_url('/aids')

        StatusList = ['Pending Translation', 'Pending Review', 'Published'];

        self.render_template('LearnAidList.html', {'aids': aids, 'count_en': count_en, 'count_other_language': count_other_language, 'StatusList':StatusList, 'StatusFilter':StatusFilter, 'languages':languages, 'langCode':langCode, 'langName':langName, 'currentuser':currentuser, 'login':login, 'logout': logout})


class LearnAidCreate(BaseHandler):

    def post(self):
        #logging.error('QQQ: templatecreate POST')
        n = LearnAids(LearnAidID = self.request.get('Name')
                  , Subject=self.request.get('Subject')
                  , Name = self.request.get('Name')
                  , LangCode = 'en'
                  , Description=self.request.get('Description')
                  , Status = 'Pending Review'
                  )
        n.put()
        return self.redirect('/aids/create')

    def get(self):
        logout = None
        login = None
        currentuser = users.get_current_user()
        if currentuser:
              logout = users.create_logout_url('/aids' )
        else:
              login = users.create_login_url('/aids')

        SubjectList = [
            'Arithmetic and Pre-Algebra: Addition and subtraction', 
            'Arithmetic and Pre-Algebra: Multiplication and division', 
            'Arithmetic and Pre-Algebra: Negative numbers',
            'Arithmetic and Pre-Algebra: Number properties',
            'Arithmetic and Pre-Algebra: Order of operations',
            'Arithmetic and Pre-Algebra: Factors and multiples',
            'Arithmetic and Pre-Algebra: Fractions',
            'Arithmetic and Pre-Algebra: Decimals',
            'Arithmetic and Pre-Algebra: Percents',
            'Arithmetic and Pre-Algebra: Ratios and proportions (basic)',
            'Arithmetic and Pre-Algebra: Exponents (basic)'
            ];		  
        self.render_template('LearnAidCreate.html', {'SubjectList': SubjectList, 'currentuser':currentuser, 'login':login, 'logout': logout})


class LearnAidEdit(BaseHandler):

    def post(self, aid_id):
        iden = int(aid_id)
        aid = ndb.Key('LearnAids', iden).get()

        currentuser = users.get_current_user()
        aid.Name = self.request.get('Name')
        aid.Subject = self.request.get('Subject')
        aid.Description = self.request.get('Description')
        VidStatusPrev = aid.VideoStatus
        aid.VideoStatus = self.request.get('VideoStatus')
        if not aid.VideoStatus == VidStatusPrev:
            aid.VideoStatusBy = currentuser
            aid.VideoStatusDate = datetime.now()    
        StatusPrev = aid.Status
        aid.Status = self.request.get('Status')
        if not aid.Status == StatusPrev:
            aid.StatusBy = currentuser
            aid.StatusDate = datetime.now()    
        aid.put()
        return self.redirect('/aids')

    def get(self, aid_id):
        iden = int(aid_id)
        aid = ndb.Key('LearnAids', iden).get()

        logout = None
        login = None
        currentuser = users.get_current_user()
        if currentuser:
              logout = users.create_logout_url('/aids' )
        else:
              login = users.create_login_url('/aids')

        SubjectList = [
            'Arithmetic and Pre-Algebra: Addition and subtraction', 
            'Arithmetic and Pre-Algebra: Multiplication and division', 
            'Arithmetic and Pre-Algebra: Negative numbers',
            'Arithmetic and Pre-Algebra: Number properties',
            'Arithmetic and Pre-Algebra: Order of operations',
            'Arithmetic and Pre-Algebra: Factors and multiples',
            'Arithmetic and Pre-Algebra: Fractions',
            'Arithmetic and Pre-Algebra: Decimals',
            'Arithmetic and Pre-Algebra: Percents',
            'Arithmetic and Pre-Algebra: Ratios and proportions (basic)',
            'Arithmetic and Pre-Algebra: Exponents (basic)'
            ];		  

        StatusList = ['Pending Translation', 'Pending Review', 'Published'];		  
        VideoStatusList = ['Pending Translation', 'Pending Review', 'Published'];		  
        self.render_template('LearnAidEdit.html', {'aid': aid, 'SubjectList': SubjectList, 'StatusList': StatusList, 'VideoStatusList': VideoStatusList, 'currentuser':currentuser, 'login':login, 'logout': logout})


class LearnAidDelete(BaseHandler):

    def get(self, aid_id):
        iden = int(aid_id)
        aid = ndb.Key('LearnAids', iden).get()
        currentuser = users.get_current_user()
#        if currentuser != template.CreatedBy and not users.is_current_user_admin():
#            self.abort(403)
#            return
        aid.key.delete()
        return self.redirect('/aids')

class LearnAidClone(BaseHandler):

    def get(self):
        if self.request.get('langCode'):
            langCode = self.request.get('langCode')

            q = LearnAids.query(LearnAids.LangCode == langCode)
            aids = q.fetch(999)

            countmap_other_language={}
            for aid in aids:
                logging.info('QQQ: LangCode in clone: %s' % aid.LangCode)
                if aid.LearnAidID not in countmap_other_language:
                    logging.info('QQQ: LearnAidID in clone: %s' % aid.LearnAidID)
                    countmap_other_language[aid.LearnAidID] = 1

            q = LearnAids.query(LearnAids.LangCode == 'en')
            aids_en = q.fetch(999)

            for aid2 in aids_en:
                if aid2.LearnAidID not in countmap_other_language:
                    logging.info('QQQ: LearnAidID to add in clone: %s' % aid2.LearnAidID)
                    logging.info('QQQ: LangCode to add in clone: %s' % langCode)
                    n = LearnAids(LearnAidID = aid2.LearnAidID
                        , Subject = aid2.Subject
                        , Name = aid2.Name
                        , VideoStatus = 'Pending Translation'
                        , LangCode = langCode
                        , Description = aid2.Description
                        , Status = 'Pending Translation'
                        )
                    n.put()
            return self.redirect('/aids')        

        else:
            return self.redirect('/aids')  