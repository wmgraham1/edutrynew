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
from models import TopicGrps
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

class TopicGrpList(BaseHandler):
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
        q = TopicGrps.query(TopicGrps.LangCode == langCode_en)
        units = q.fetch(999)
        for unit in units:
            logging.info('QQQ: count_en: %d' % count_en)
            count_en = count_en + 1
        logging.info('QQQ: Total count_en: %d' % count_en)

        logging.info('QQQ: langCode: %s' % langCode)
        count_other_language = 0
        q2 = TopicGrps.query(TopicGrps.LangCode == langCode)
        unitsx = q2.fetch(999)
        for unit in unitsx:
            logging.info('QQQ: count_other_language: %d' % count_other_language)
            count_other_language = count_other_language + 1
        logging.info('QQQ: Total count_other_language: %d' % count_other_language)

        logging.info('GGG: StatusFilter in LearnUnitList: %s' % StatusFilter)
        if StatusFilter == 'all':
            if SubjFilter == 'all':
                q = TopicGrps.query(TopicGrps.LangCode == langCode).order(TopicGrps.Seq, TopicGrps.LearningUnitID)
            else:
                q = TopicGrps.query(TopicGrps.LangCode == langCode, TopicGrps.Subject == SubjFilter).order(TopicGrps.Seq, TopicGrps.LearningUnitID)
        else:
            if SubjFilter == 'all':
                q = TopicGrps.query(TopicGrps.LangCode == langCode, TopicGrps.Status == StatusFilter).order(TopicGrps.Seq, TopicGrps.LearningUnitID)
            else:
                q = TopicGrps.query(TopicGrps.LangCode == langCode, TopicGrps.Status == StatusFilter, TopicGrps.Subject == SubjFilter).order(TopicGrps.Seq, TopicGrps.LearningUnitID)

        units = q.fetch(999)

        q4 = Subjects.query(Subjects.LangCode == langCode, Subjects.Subject == SubjFilter).order(Subjects.Seq)
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
              logout = users.create_logout_url('/topgrps' )
        else:
              login = users.create_login_url('/topgrps')

        StatusList = ['Pending Translation', 'Pending Review', 'Published'];
#        SubjectList = ['Math', 'Science'];	
        self.render_template('LearnTopicGrpList.html', {'units': units, 'count_en': count_en, 'count_other_language': count_other_language, 'StatusList':StatusList, 'SubjectList':SubjectList, 'StatusFilter':StatusFilter, 'SubjFilter':SubjFilter, 'languages':languages, 'langCode':langCode, 'langName':langName, 'currentuser':currentuser, 'login':login, 'logout': logout})


class TopicGrpEditList(BaseHandler):
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
        q = TopicGrps.query(TopicGrps.LangCode == langCode_en)
        units = q.fetch(999)
        for unit in units:
            logging.info('QQQ: count_en: %d' % count_en)
            count_en = count_en + 1
        logging.info('QQQ: Total count_en: %d' % count_en)

        logging.info('QQQ: langCode: %s' % langCode)
        count_other_language = 0
        q2 = TopicGrps.query(TopicGrps.LangCode == langCode)
        unitsx = q2.fetch(999)
        for unit in unitsx:
            logging.info('QQQ: count_other_language: %d' % count_other_language)
            count_other_language = count_other_language + 1
        logging.info('QQQ: Total count_other_language: %d' % count_other_language)

        logging.info('GGG: StatusFilter in LearnUnitList: %s' % StatusFilter)
        if StatusFilter == 'all':
            if SubjFilter == 'all':
                q = TopicGrps.query(TopicGrps.LangCode == langCode).order(TopicGrps.Seq, TopicGrps.LearningUnitID)
            else:
                q = TopicGrps.query(TopicGrps.LangCode == langCode, TopicGrps.Subject == SubjFilter).order(TopicGrps.Seq, TopicGrps.LearningUnitID)
        else:
            if SubjFilter == 'all':
                q = TopicGrps.query(TopicGrps.LangCode == langCode, TopicGrps.Status == StatusFilter).order(TopicGrps.Seq, TopicGrps.LearningUnitID)
            else:
                q = TopicGrps.query(TopicGrps.LangCode == langCode, TopicGrps.Status == StatusFilter, TopicGrps.Subject == SubjFilter).order(TopicGrps.Seq, TopicGrps.LearningUnitID)
        units = q.fetch(999)

        if StatusFilter == 'all':
            if SubjFilter == 'all':
                f = TopicGrps.query(TopicGrps.LangCode == 'en')
            else:
                f = TopicGrps.query(TopicGrps.LangCode == 'en', TopicGrps.Subject == SubjFilter)
        else:
            if SubjFilter == 'all':
                f = TopicGrps.query(TopicGrps.LangCode == 'en', TopicGrps.Status == StatusFilter)
            else:
                f = TopicGrps.query(TopicGrps.LangCode == 'en', TopicGrps.Status == StatusFilter, TopicGrps.Subject == SubjFilter)
        units_en = f.fetch(999)
        
        dict_units_en = {}
        for unit_en in units_en:
#            logging.info('GGG: Subjects.py/LearningUnitID: %s' % unit_en.LearningUnitID)
#            logging.info('GGG: Subjects.py/Description: %s' % unit_en.Description)
            dict_units_en[unit_en.LearningUnitID] = unit_en.Description


        q4 = Subjects.query(Subjects.LangCode == langCode, Subjects.Subject == SubjFilter).order(Subjects.Seq)
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
              logout = users.create_logout_url('/topgrps' )
        else:
              login = users.create_login_url('/topgrps')

        StatusList = ['Pending Translation', 'Pending Review', 'Published'];
#        SubjectList = ['Math', 'Science'];	
        self.render_template('LearnTopicGrpListEdit.html', {'units': units, 'count_en': count_en, 'count_other_language': count_other_language, 'StatusList':StatusList, 'SubjectList':SubjectList, 'StatusFilter':StatusFilter, 'dict_units_en':dict_units_en, 'SubjFilter':SubjFilter, 'languages':languages, 'langCode':langCode, 'langName':langName, 'currentuser':currentuser, 'login':login, 'logout': logout})


class TopicGrpCreate(BaseHandler):
    def post(self):
        #logging.error('QQQ: templatecreate POST')
        Subject=self.request.get('Subject')
        n = TopicGrps(LearningUnitID = self.request.get('Name')
                  , Subject=Subject
                  , Name = self.request.get('Name')
                  , Seq = 999
                  , LangCode = 'en'
                  , Description=self.request.get('Description')
                  , Status = 'Pending Review'
                  )
        n.put()
        return self.redirect('/topgrps/create?SubjFilter=' + Subject)

    def get(self):
        if self.request.get('SubjFilter'):
            SubjFilter=self.request.get('SubjFilter')
            self.session['SubjFilter'] = SubjFilter
        else:
            SubjFilter = self.session.get('SubjFilter')
        if not SubjFilter:
            self.session['SubjFilter'] = 'all'
            SubjFilter = 'all'

        if self.request.get('SubjAreaFilter'):
            SubjAreaFilter=self.request.get('SubjAreaFilter')
            self.session['SubjAreaFilter'] = SubjAreaFilter
        else:
            SubjAreaFilter = self.session.get('SubjAreaFilter')
        if not SubjAreaFilter:
            self.session['SubjAreaFilter'] = 'Math'
            SubjAreaFilter = 'Math'

        logout = None
        login = None
        currentuser = users.get_current_user()
        if currentuser:
              logout = users.create_logout_url('/topgrps' )
        else:
              login = users.create_login_url('/topgrps')

        q3 = Subjects.query(Subjects.Subject == SubjAreaFilter, Subjects.LangCode == 'en').order(Subjects.Seq, Subjects.LearningUnitID)
        subjects = q3.fetch(999)
        SubjectList = []
        if subjects:
            for subject in subjects:
                SubjectList.append(subject.Name)
        else:
            SubjectList.append('none')
            
#        SubjectList = ['Math', 'Biology', 'Chemistry'];		  
        self.render_template('LearnTopicGrpCreate.html', {'SubjectList':SubjectList, 'SubjFilter':SubjFilter, 'currentuser':currentuser, 'login':login, 'logout': logout})

class TopicGrpEditListPost(BaseHandler):
    def post(self, unit_id):
        logging.info('QQQ: TopicGrpEditListPost: %s' % unit_id)
        iden = int(unit_id)
        unit = ndb.Key('TopicGrps', iden).get()

        currentuser = users.get_current_user()
        unit.Name = self.request.get('Name')
        if self.request.get('Seq') != 'None':
            unit.Seq = int(self.request.get('Seq'))
        unit.Subject = self.request.get('Subject')
        unit.Description = self.request.get('Description')
        StatusPrev = unit.Status
        unit.Status = self.request.get('Status')
        if not unit.Status == StatusPrev:
            unit.StatusBy = currentuser
            unit.StatusDate = datetime.now()    
        unit.put()
#        return self.redirect('/topgrps')

class TopicGrpEdit(BaseHandler):
    def post(self, unit_id):
        iden = int(unit_id)
        unit = ndb.Key('TopicGrps', iden).get()

        currentuser = users.get_current_user()
        unit.Name = self.request.get('Name')
        if self.request.get('Seq') != 'None':
            unit.Seq = int(self.request.get('Seq'))
        unit.Subject = self.request.get('Subject')
        unit.Description = self.request.get('Description')
        StatusPrev = unit.Status
        unit.Status = self.request.get('Status')
        if not unit.Status == StatusPrev:
            unit.StatusBy = currentuser
            unit.StatusDate = datetime.now()    
        unit.put()
        return self.redirect('/topgrps')

    def get(self, unit_id):
        iden = int(unit_id)
        unit = ndb.Key('TopicGrps', iden).get()

        f = TopicGrps.query(TopicGrps.LangCode == 'en', TopicGrps.LearningUnitID == unit.LearningUnitID)
        units_en = f.get()

        if self.request.get('SubjFilter'):
            SubjFilter=self.request.get('SubjFilter')
            self.session['SubjFilter'] = SubjFilter
        else:
            SubjFilter = self.session.get('SubjFilter')
        if not SubjFilter:
            self.session['SubjFilter'] = 'all'
            SubjFilter = 'all'
        logging.info('QQQ: SubjFilter in Topic Grp Edit: %s' % SubjFilter)

        if self.request.get('SubjAreaFilter'):
            SubjAreaFilter=self.request.get('SubjAreaFilter')
            self.session['SubjAreaFilter'] = SubjAreaFilter
        else:
            SubjAreaFilter = self.session.get('SubjAreaFilter')
        if not SubjAreaFilter:
            self.session['SubjAreaFilter'] = 'Math'
            SubjAreaFilter = 'Math'

        q3 = Subjects.query(Subjects.Subject == SubjAreaFilter).order(Subjects.Seq)
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
              logout = users.create_logout_url('/topgrps' )
        else:
              login = users.create_login_url('/topgrps')

#        SubjectList = ['Math', 'Biology', 'Chemistry'];		  
        StatusList = ['Pending Translation', 'Pending Review', 'Published'];		  
        self.render_template('LearnTopicGrpEdit.html', {'unit': unit, 'units_en': units_en, 'SubjectList': SubjectList, 'SubjFilter': SubjFilter, 'StatusList': StatusList, 'currentuser':currentuser, 'login':login, 'logout': logout})


class TopicGrpDelete(BaseHandler):
    def get(self, unit_id):
        iden = int(unit_id)
        unit = ndb.Key('TopicGrps', iden).get()
        currentuser = users.get_current_user()
#        if currentuser != template.CreatedBy and not users.is_current_user_admin():
#            self.abort(403)
#            return
        unit.key.delete()
        return self.redirect('/topgrps')

class TopicGrpClone(BaseHandler):
    def get(self):
        if self.request.get('langCode'):
            langCode = self.request.get('langCode')

            q = TopicGrps.query(TopicGrps.LangCode == langCode)
            units = q.fetch(999)

            countmap_other_language={}
            for unit in units:
                logging.info('QQQ: LangCode in clone: %s' % unit.LangCode)
                if unit.LearningUnitID not in countmap_other_language:
                    logging.info('QQQ: LearningUnitID in clone: %s' % unit.LearningUnitID)
                    countmap_other_language[unit.LearningUnitID] = 1

            q = TopicGrps.query(TopicGrps.LangCode == 'en')
            units_en = q.fetch(999)

            for unit2 in units_en:
                if unit2.LearningUnitID not in countmap_other_language:
                    logging.info('QQQ: LearningUnitID to add in clone: %s' % unit2.LearningUnitID)
                    logging.info('QQQ: LangCode to add in clone: %s' % langCode)
                    n = TopicGrps(LearningUnitID = unit2.LearningUnitID
                        , Subject = unit2.Subject
                        , Seq = unit2.Seq
                        , Name = unit2.Name
                        , LangCode = langCode
                        , Description = unit2.Description
                        , Status = 'Pending Translation'
                        )
                    n.put()
            return self.redirect('/topgrps')        

        else:
            return self.redirect('/topgrps')  