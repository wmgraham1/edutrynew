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


from models import LearningUnits
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

class LearnUnitList(BaseHandler):

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

        if self.request.get('TopGrpFilter'):
            TopGrpFilter=self.request.get('TopGrpFilter')
            self.session['TopGrpFilter'] = TopGrpFilter
        else:
            TopGrpFilter = self.session.get('TopGrpFilter')
        if not TopGrpFilter:
            self.session['TopGrpFilter'] = 'all'
            TopGrpFilter = 'all'

        count_en = 0
        langCode_en = 'en'
        q = LearningUnits.query(LearningUnits.LangCode == langCode_en)
        units = q.fetch(999)
        for unit in units:
#            logging.info('QQQ: count_en: %d' % count_en)
            count_en = count_en + 1
        logging.info('QQQ: Total count_en: %d' % count_en)

        logging.info('QQQ: langCode: %s' % langCode)
        count_other_language = 0
        q2 = LearningUnits.query(LearningUnits.LangCode == langCode)
        unitsx = q2.fetch(999)
        for unit in unitsx:
#            logging.info('QQQ: count_other_language: %d' % count_other_language)
            count_other_language = count_other_language + 1
        logging.info('QQQ: Total count_other_language: %d' % count_other_language)

        logging.info('LLL: StatusFilter in LearnUnitList: %s' % StatusFilter)
        logging.info('LLL: TopGrpFilter in LearnUnitList: %s' % TopGrpFilter)
        logging.info('LLL: langCode in LearnUnitList: %s' % langCode)
        #TopGrpFilter = 'all'
        #StatusFilter = 'all'
        if StatusFilter == 'all':
            if TopGrpFilter == 'all':
                logging.info('LLL: in LearnUnitList: now in all/all')
                q = LearningUnits.query(LearningUnits.LangCode == 'en').order(LearningUnits.LearningUnitID)
            else:
                logging.info('LLL: in LearnUnitList: now in all/TopGrpFilter')
                q = LearningUnits.query(LearningUnits.LangCode == langCode, LearningUnits.Subject == TopGrpFilter).order(LearningUnits.LearningUnitID)
        else:
            if TopGrpFilter == 'all':
                logging.info('LLL: in LearnUnitList: now in StatusFilter/all')
                q = LearningUnits.query(LearningUnits.LangCode == langCode, LearningUnits.Status == StatusFilter).order(LearningUnits.LearningUnitID)
            else:
                logging.info('LLL: in LearnUnitList: now in StatusFilter/TopGrpFilter')
                q = LearningUnits.query(LearningUnits.LangCode == langCode, LearningUnits.Status == StatusFilter, LearningUnits.Subject == TopGrpFilter).order(LearningUnits.LearningUnitID)
#        q = LearningUnits.query(LearningUnits.LangCode == langCode_en, LearningUnits.Subject == 'Math').order(LearningUnits.LearningUnitID)
        logging.info('LLL: q in LearnUnitList: %s' % q)

        units = q.fetch(999)
        unitcnt = 0
        for uni in units:
            logging.info('QQQ: uni.LearningUnitID in LearnUnitList: %s' % uni.LearningUnitID)
            unitcnt = unitcnt + 1
        logging.info('QQQ: unitcnt in LearnUnitList: %d' % unitcnt)    

        logout = None
        login = None
        currentuser = users.get_current_user()
        if currentuser:
              logout = users.create_logout_url('/units' )
        else:
              login = users.create_login_url('/units')

        StatusList = ['Pending Translation', 'Pending Review', 'Published'];

        self.render_template('LearnUnitList.html', {'units': units, 'count_en': count_en, 'count_other_language': count_other_language, 'StatusList':StatusList, 'StatusFilter':StatusFilter, 'SubjFilter':SubjFilter, 'TopGrpFilter':TopGrpFilter, 'languages':languages, 'langCode':langCode, 'langName':langName, 'currentuser':currentuser, 'login':login, 'logout': logout})

class LearnUnitEditList(BaseHandler):

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

        if self.request.get('TopGrpFilter'):
            TopGrpFilter=self.request.get('TopGrpFilter')
            self.session['TopGrpFilter'] = TopGrpFilter
        else:
            TopGrpFilter = self.session.get('TopGrpFilter')
        if not TopGrpFilter:
            self.session['TopGrpFilter'] = 'all'
            TopGrpFilter = 'all'

        TopGrpList = []
        q = TopicGrps.query(TopicGrps.LangCode == 'en').order(TopicGrps.Seq)
        SubjAreaResponseSet = q.fetch(999)
        for SubjArea in SubjAreaResponseSet:
            TopGrpList.append(SubjArea.Name)

        count_en = 0
        langCode_en = 'en'
        q = LearningUnits.query(LearningUnits.LangCode == langCode_en)
        units = q.fetch(999)
        for unit in units:
#            logging.info('QQQ: count_en: %d' % count_en)
            count_en = count_en + 1
        logging.info('QQQ: Total count_en: %d' % count_en)

        logging.info('QQQ: langCode: %s' % langCode)
        count_other_language = 0
        q2 = LearningUnits.query(LearningUnits.LangCode == langCode)
        unitsx = q2.fetch(999)
        for unit in unitsx:
#            logging.info('QQQ: count_other_language: %d' % count_other_language)
            count_other_language = count_other_language + 1
        logging.info('QQQ: Total count_other_language: %d' % count_other_language)

        logging.info('LLL: StatusFilter in LearnUnitList: %s' % StatusFilter)
        logging.info('LLL: TopGrpFilter in LearnUnitList: %s' % TopGrpFilter)
        logging.info('LLL: langCode in LearnUnitList: %s' % langCode)
        #TopGrpFilter = 'all'
        #StatusFilter = 'all'
        if StatusFilter == 'all':
            if TopGrpFilter == 'all':
                logging.info('LLL: in LearnUnitList: now in all/all')
                q = LearningUnits.query(LearningUnits.LangCode == 'en').order(LearningUnits.LearningUnitID) #LearningUnits.Seq, 
            else:
                logging.info('LLL: in LearnUnitList: now in all/TopGrpFilter')
                q = LearningUnits.query(LearningUnits.LangCode == langCode, LearningUnits.Subject == TopGrpFilter).order(LearningUnits.LearningUnitID)
        else:
            if TopGrpFilter == 'all':
                logging.info('LLL: in LearnUnitList: now in StatusFilter/all')
                q = LearningUnits.query(LearningUnits.LangCode == langCode, LearningUnits.Status == StatusFilter).order(LearningUnits.LearningUnitID)
            else:
                logging.info('LLL: in LearnUnitList: now in StatusFilter/TopGrpFilter')
                q = LearningUnits.query(LearningUnits.LangCode == langCode, LearningUnits.Status == StatusFilter, LearningUnits.Subject == TopGrpFilter).order(LearningUnits.LearningUnitID)
#        q = LearningUnits.query(LearningUnits.LangCode == langCode_en, LearningUnits.Subject == 'Math').order(LearningUnits.LearningUnitID)
        logging.info('LLL: q in LearnUnitList: %s' % q)

        units = q.fetch(999)
        unitcnt = 0
        for uni in units:
            logging.info('QQQ: uni.LearningUnitID in LearnUnitList: %s' % uni.LearningUnitID)
            unitcnt = unitcnt + 1
        logging.info('QQQ: unitcnt in LearnUnitList: %d' % unitcnt)    

        logout = None
        login = None
        currentuser = users.get_current_user()
        if currentuser:
              logout = users.create_logout_url('/units' )
        else:
              login = users.create_login_url('/units')

        StatusList = ['Pending Translation', 'Pending Review', 'Published'];

        self.render_template('LearnUnitListEdit.html', {'units': units, 'count_en': count_en, 'count_other_language': count_other_language, 'TopGrpList':TopGrpList, 'StatusList':StatusList, 'StatusFilter':StatusFilter, 'SubjFilter':SubjFilter, 'TopGrpFilter':TopGrpFilter, 'languages':languages, 'langCode':langCode, 'langName':langName, 'currentuser':currentuser, 'login':login, 'logout': logout})


class LearnUnitCreate(BaseHandler):

    def post(self):
        #logging.error('QQQ: templatecreate POST')
        n = LearningUnits(LearningUnitID = self.request.get('Name')
                  , Subject=self.request.get('Subject')
                  , Name = self.request.get('Name')
                  , LangCode = 'en'
                  , Description=self.request.get('Description')
                  , Status = 'Pending Review'
                  )
        n.put()
        return self.redirect('/units/create')

    def get(self):
        logout = None
        login = None
        currentuser = users.get_current_user()
        if currentuser:
              logout = users.create_logout_url('/units' )
        else:
              login = users.create_login_url('/units')

        if self.request.get('SubjFilter'):
            SubjFilter=self.request.get('SubjFilter')
            self.session['SubjFilter'] = SubjFilter
        else:
            SubjFilter = self.session.get('SubjFilter')
        if not SubjFilter:
            self.session['SubjFilter'] = 'all'
            SubjFilter = 'all'
        logging.info('QQQ: SubjFilter in Topic Grp Edit: %s' % SubjFilter)

        if self.request.get('TopGrpFilter'):
            TopGrpFilter=self.request.get('TopGrpFilter')
            self.session['TopGrpFilter'] = TopGrpFilter
        else:
            TopGrpFilter = self.session.get('TopGrpFilter')
        if not TopGrpFilter:
            self.session['TopGrpFilter'] = 'all'
            TopGrpFilter = 'all'

        logging.info('QQQ: SubjFilter in Topic Grp Edit: %s' % SubjFilter)
        q3 = TopicGrps.query(TopicGrps.Subject == SubjFilter).order(TopicGrps.Seq)
        subjects = q3.fetch(999)
        SubjectList = []
        TknGrpCnt = 0
        if subjects:
            for subject in subjects:
                TknGrpCnt = TknGrpCnt + 1
                logging.info('QQQ: TopicGrpList in Topic Grp List Build: %s' % subject.Name)
                SubjectList.append(subject.Name)
        else:
            SubjectList.append('none')
        logging.info('QQQ: TknGrpCnt in Topic Grp List Build: %d' % TknGrpCnt)
        
#        SubjectList = ['Math', 'Biology', 'Chemistry'];		  
        self.render_template('LearnUnitCreate.html', {'SubjectList': SubjectList, 'TopGrpFilter': TopGrpFilter, 'currentuser':currentuser, 'login':login, 'logout': logout})


class LearnUnitEditListPost(BaseHandler):
    def post(self, unit_id):
        iden = int(unit_id)
        unit = ndb.Key('LearningUnits', iden).get()

        currentuser = users.get_current_user()
        unit.TemplateName = self.request.get('TemplateName')
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
        logging.info("XXXXXXXXXXxxxx id: %s" % iden)
        logging.info("XXXXXXXXXXxxxxSeq: %s" % self.request.get('Seq'))
        unit.put()
        
class LearnUnitEdit(BaseHandler):

    def post(self, unit_id):
        iden = int(unit_id)
        unit = ndb.Key('LearningUnits', iden).get()

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
        return self.redirect('/units')

    def get(self, unit_id):
        iden = int(unit_id)
        unit = ndb.Key('LearningUnits', iden).get()

        if self.request.get('SubjFilter'):
            SubjFilter=self.request.get('SubjFilter')
            self.session['SubjFilter'] = SubjFilter
        else:
            SubjFilter = self.session.get('SubjFilter')
        if not SubjFilter:
            self.session['SubjFilter'] = 'all'
            SubjFilter = 'all'
        logging.info('QQQ: SubjFilter in Topic Grp Edit: %s' % SubjFilter)

        q3 = TopicGrps.query(TopicGrps.Subject == SubjFilter).order(TopicGrps.Seq)
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
              logout = users.create_logout_url('/units' )
        else:
              login = users.create_login_url('/units')

#        SubjectList = ['Math', 'Biology', 'Chemistry'];		  
        StatusList = ['Pending Translation', 'Pending Review', 'Published'];		  
        self.render_template('LearnUnitEdit.html', {'unit': unit, 'SubjectList': SubjectList, 'StatusList': StatusList, 'currentuser':currentuser, 'login':login, 'logout': logout})


class LearnUnitDelete(BaseHandler):

    def get(self, unit_id):
        iden = int(unit_id)
        unit = ndb.Key('LearningUnits', iden).get()
        currentuser = users.get_current_user()
#        if currentuser != template.CreatedBy and not users.is_current_user_admin():
#            self.abort(403)
#            return
        unit.key.delete()
        return self.redirect('/units')

class LearnUnitClone(BaseHandler):

    def get(self):
        if self.request.get('langCode'):
            langCode = self.request.get('langCode')

            q = LearningUnits.query(LearningUnits.LangCode == langCode)
            units = q.fetch(999)

            countmap_other_language={}
            for unit in units:
                logging.info('QQQ: LangCode in clone: %s' % unit.LangCode)
                if unit.LearningUnitID not in countmap_other_language:
                    logging.info('QQQ: LearningUnitID in clone: %s' % unit.LearningUnitID)
                    countmap_other_language[unit.LearningUnitID] = 1

            q = LearningUnits.query(LearningUnits.LangCode == 'en')
            units_en = q.fetch(999)

            for unit2 in units_en:
                if unit2.LearningUnitID not in countmap_other_language:
                    logging.info('QQQ: LearningUnitID to add in clone: %s' % unit2.LearningUnitID)
                    logging.info('QQQ: LangCode to add in clone: %s' % langCode)
                    n = LearningUnits(LearningUnitID = unit2.LearningUnitID
                        , Subject = unit2.Subject
                        , Name = unit2.Name
                        , LangCode = langCode
                        , Description = unit2.Description
                        , Status = 'Pending Translation'
                        )
                    n.put()
            return self.redirect('/units')        

        else:
            return self.redirect('/units')  