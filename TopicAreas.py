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


from models import Subjects
from models import TopicAreas
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

class TopicAreaList(BaseHandler):

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

        if self.request.get('SubjFilter'):
            SubjFilter=self.request.get('SubjFilter')
            self.session['SubjFilter'] = SubjFilter
        else:
            SubjFilter = self.session.get('SubjFilter')
        if not SubjFilter:
            self.session['SubjFilter'] = 'all'
            SubjFilter = 'all'

        count_en = 0
        langCode_en = 'en'
        q = TopicAreas.query(TopicAreas.LangCode == langCode_en)
        units = q.fetch(999)
        for unit in units:
            logging.info('QQQ: count_en: %d' % count_en)
            count_en = count_en + 1
        logging.info('QQQ: Total count_en: %d' % count_en)

        logging.info('QQQ: langCode: %s' % langCode)
        count_other_language = 0
        q2 = TopicAreas.query(TopicAreas.LangCode == langCode)
        unitsx = q2.fetch(999)
        for unit in unitsx:
            logging.info('QQQ: count_other_language: %d' % count_other_language)
            count_other_language = count_other_language + 1
        logging.info('QQQ: Total count_other_language: %d' % count_other_language)

        logging.info('GGG: StatusFilter in LearnUnitList: %s' % StatusFilter)
        if StatusFilter == 'all':
            if SubjFilter == 'all':
                q = TopicAreas.query(TopicAreas.LangCode == langCode).order(TopicAreas.LearningUnitID)
            else:
                q = TopicAreas.query(TopicAreas.LangCode == langCode, TopicAreas.Subject == SubjFilter).order(TopicAreas.LearningUnitID)
        else:
            if SubjFilter == 'all':
                q = TopicAreas.query(TopicAreas.LangCode == langCode, TopicAreas.Status == StatusFilter).order(TopicAreas.LearningUnitID)
            else:
                q = TopicAreas.query(TopicAreas.LangCode == langCode, TopicAreas.Status == StatusFilter, TopicAreas.Subject == SubjFilter).order(TopicAreas.LearningUnitID)

        units = q.fetch(999)

        q4 = Subjects.query(Subjects.Subject == 'Math')
        subjects = q4.fetch(999)
        SubjectList = []
        if subjects:
            for subject in subjects:
                SubjectList.append(subject.Name)
        else:
            SubjectList.append('none')
            
        logout = None
        login = None
        currentuser = users.get_current_user()
        if currentuser:
              logout = users.create_logout_url('/topareas' )
        else:
              login = users.create_login_url('/topareas')

        StatusList = ['Pending Translation', 'Pending Review', 'Published'];
#        SubjectList = ['Math', 'Science'];	
        self.render_template('LearnTopicAreaList.html', {'units': units, 'count_en': count_en, 'count_other_language': count_other_language, 'StatusList':StatusList, 'SubjectList':SubjectList, 'StatusFilter':StatusFilter, 'SubjFilter':SubjFilter, 'languages':languages, 'langCode':langCode, 'langName':langName, 'currentuser':currentuser, 'login':login, 'logout': logout})


class TopicAreaCreate(BaseHandler):

    def post(self):
        #logging.error('QQQ: templatecreate POST')
        n = TopicAreas(LearningUnitID = self.request.get('Name')
                  , Subject=self.request.get('Subject')
                  , Name = self.request.get('Name')
                  , LangCode = 'en'
                  , Description=self.request.get('Description')
                  , Status = 'Pending Review'
                  )
        n.put()
        return self.redirect('/topareas/create')

    def get(self):
        logout = None
        login = None
        currentuser = users.get_current_user()
        if currentuser:
              logout = users.create_logout_url('/subjs' )
        else:
              login = users.create_login_url('/subjs')

        q3 = Subjects.query(Subjects.Subject == 'Math')
        subjects = q3.fetch(999)
        SubjectList = []
        if subjects:
            for subject in subjects:
                SubjectList.append(subject.Name)
        else:
            SubjectList.append('none')
            
#        SubjectList = ['Math', 'Biology', 'Chemistry'];		  
        self.render_template('LearnTopicAreaCreate.html', {'SubjectList': SubjectList, 'currentuser':currentuser, 'login':login, 'logout': logout})


class TopicAreaEdit(BaseHandler):

    def post(self, unit_id):
        iden = int(unit_id)
        unit = ndb.Key('TopicAreas', iden).get()

        currentuser = users.get_current_user()
        unit.Name = self.request.get('Name')
        unit.Subject = self.request.get('Subject')
        unit.Description = self.request.get('Description')
        StatusPrev = unit.Status
        unit.Status = self.request.get('Status')
        if not unit.Status == StatusPrev:
            unit.StatusBy = currentuser
            unit.StatusDate = datetime.now()    
        unit.put()
        return self.redirect('/topareas')

    def get(self, unit_id):
        iden = int(unit_id)
        unit = ndb.Key('TopicAreas', iden).get()

        q3 = Subjects.query(Subjects.Subject == 'Math')
        subjects = q3.fetch(999)
        SubjectList = []
        if subjects:
            for subject in subjects:
                SubjectList.append(subject.Name)
        else:
            SubjectList.append('none')
        
        logout = None
        login = None
        currentuser = users.get_current_user()
        if currentuser:
              logout = users.create_logout_url('/topareas' )
        else:
              login = users.create_login_url('/topareas')

#        SubjectList = ['Math', 'Biology', 'Chemistry'];		  
        StatusList = ['Pending Translation', 'Pending Review', 'Published'];		  
        self.render_template('LearnTopicAreaEdit.html', {'unit': unit, 'SubjectList': SubjectList, 'StatusList': StatusList, 'currentuser':currentuser, 'login':login, 'logout': logout})


class TopicAreaDelete(BaseHandler):

    def get(self, unit_id):
        iden = int(unit_id)
        unit = ndb.Key('TopicAreas', iden).get()
        currentuser = users.get_current_user()
#        if currentuser != template.CreatedBy and not users.is_current_user_admin():
#            self.abort(403)
#            return
        unit.key.delete()
        return self.redirect('/topareas')

class TopicAreaClone(BaseHandler):

    def get(self):
        if self.request.get('langCode'):
            langCode = self.request.get('langCode')

            q = TopicAreas.query(TopicAreas.LangCode == langCode)
            units = q.fetch(999)

            countmap_other_language={}
            for unit in units:
                logging.info('QQQ: LangCode in clone: %s' % unit.LangCode)
                if unit.LearningUnitID not in countmap_other_language:
                    logging.info('QQQ: LearningUnitID in clone: %s' % unit.LearningUnitID)
                    countmap_other_language[unit.LearningUnitID] = 1

            q = TopicAreas.query(TopicAreas.LangCode == 'en')
            units_en = q.fetch(999)

            for unit2 in units_en:
                if unit2.LearningUnitID not in countmap_other_language:
                    logging.info('QQQ: LearningUnitID to add in clone: %s' % unit2.LearningUnitID)
                    logging.info('QQQ: LangCode to add in clone: %s' % langCode)
                    n = TopicAreas(LearningUnitID = unit2.LearningUnitID
                        , Subject = unit2.Subject
                        , Name = unit2.Name
                        , LangCode = langCode
                        , Description = unit2.Description
                        , Status = 'Pending Translation'
                        )
                    n.put()
            return self.redirect('/topareas')        

        else:
            return self.redirect('/topareas')  