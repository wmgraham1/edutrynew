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


from models import SubjectAreas
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

class SubjAreaList(BaseHandler):

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

        if self.request.get('Typ'):
            Typ=self.request.get('Typ')
            self.session['Typ'] = Typ
        else:
            Typ = self.session.get('Typ')
        if not Typ:
            self.session['Typ'] = 'ex'
            Typ = 'ex'

        count_en = 0
        langCode_en = 'en'
        q = SubjectAreas.query(SubjectAreas.LangCode == langCode_en)
        units = q.fetch(999)
        for unit in units:
            logging.info('QQQ: count_en: %d' % count_en)
            count_en = count_en + 1
        logging.info('QQQ: Total count_en: %d' % count_en)

        logging.info('QQQ: langCode: %s' % langCode)
        count_other_language = 0
        q2 = SubjectAreas.query(SubjectAreas.LangCode == langCode)
        unitsx = q2.fetch(999)
        for unit in unitsx:
            logging.info('QQQ: count_other_language: %d' % count_other_language)
            count_other_language = count_other_language + 1
        logging.info('QQQ: Total count_other_language: %d' % count_other_language)

        logging.info('GGG: StatusFilter in SubjAreasList: %s' % StatusFilter)
        if StatusFilter == 'all':
            q = SubjectAreas.query(SubjectAreas.LangCode == langCode).order(SubjectAreas.Seq, SubjectAreas.LearningUnitID)
        else:
            q = SubjectAreas.query(SubjectAreas.LangCode == langCode, SubjectAreas.Status == StatusFilter).order(SubjectAreas.Seq, SubjectAreas.LearningUnitID)
        units = q.fetch(999)

        logout = None
        login = None
        currentuser = users.get_current_user()
        if currentuser:
              logout = users.create_logout_url('/subjareas' )
        else:
              login = users.create_login_url('/subjareas')

        StatusList = ['Pending Translation', 'Pending Review', 'Published'];

        self.render_template('LearnSubjAreaList.html', {'units': units, 'Typ': Typ, 'count_en': count_en, 'count_other_language': count_other_language, 'StatusList':StatusList, 'StatusFilter':StatusFilter, 'languages':languages, 'langCode':langCode, 'langName':langName, 'currentuser':currentuser, 'login':login, 'logout': logout})


class SubjAreaCreate(BaseHandler):

    def post(self):
        #logging.error('QQQ: templatecreate POST')
        n = SubjectAreas(LearningUnitID = self.request.get('Name')
#                  , Subject=self.request.get('Subject')
                  , Name = self.request.get('Name')
                  , Seq = 999
                  , LangCode = 'en'
                  , Description=self.request.get('Description')
                  , Status = 'Pending Review'
                  )
        n.put()
        return self.redirect('/subjareas/create')

    def get(self):
        logout = None
        login = None
        currentuser = users.get_current_user()
        if currentuser:
              logout = users.create_logout_url('/subjareas' )
        else:
              login = users.create_login_url('/subjareas')

#        SubjectList = ['Math', 'Biology', 'Chemistry'];		  
        self.render_template('LearnSubjAreaCreate.html', {'currentuser':currentuser, 'login':login, 'logout': logout})


class SubjAreaEdit(BaseHandler):

    def post(self, unit_id):
        iden = int(unit_id)
        unit = ndb.Key('SubjectAreas', iden).get()

        currentuser = users.get_current_user()
        unit.Name = self.request.get('Name')
        if self.request.get('Seq') != 'None':
            unit.Seq = int(self.request.get('Seq'))
#        unit.Subject = self.request.get('Subject')
        unit.Description = self.request.get('Description')
        StatusPrev = unit.Status
        unit.Status = self.request.get('Status')
        if not unit.Status == StatusPrev:
            unit.StatusBy = currentuser
            unit.StatusDate = datetime.now()    
        unit.put()
        return self.redirect('/subjareas')

    def get(self, unit_id):
        iden = int(unit_id)
        unit = ndb.Key('SubjectAreas', iden).get()

        logout = None
        login = None
        currentuser = users.get_current_user()
        if currentuser:
              logout = users.create_logout_url('/subjareas' )
        else:
              login = users.create_login_url('/subjareas')

#        SubjectList = ['Math', 'Biology', 'Chemistry'];		  
        StatusList = ['Pending Translation', 'Pending Review', 'Published'];		  
#        self.render_template('LearnSubjAreaEdit.html', {'unit': unit, 'SubjectList': SubjectList, 'StatusList': StatusList, 'currentuser':currentuser, 'login':login, 'logout': logout})
        self.render_template('LearnSubjAreaEdit.html', {'unit': unit, 'StatusList': StatusList, 'currentuser':currentuser, 'login':login, 'logout': logout})


class SubjAreaDelete(BaseHandler):

    def get(self, unit_id):
        iden = int(unit_id)
        unit = ndb.Key('SubjectAreas', iden).get()
        currentuser = users.get_current_user()
#        if currentuser != template.CreatedBy and not users.is_current_user_admin():
#            self.abort(403)
#            return
        unit.key.delete()
        return self.redirect('/subjareas')

class SubjAreaClone(BaseHandler):

    def get(self):
        if self.request.get('langCode'):
            langCode = self.request.get('langCode')

            q = SubjectAreas.query(SubjectAreas.LangCode == langCode)
            units = q.fetch(999)

            countmap_other_language={}
            for unit in units:
                logging.info('QQQ: LangCode in clone: %s' % unit.LangCode)
                if unit.LearningUnitID not in countmap_other_language:
                    logging.info('QQQ: LearningUnitID in clone: %s' % unit.LearningUnitID)
                    countmap_other_language[unit.LearningUnitID] = 1

            q = SubjectAreas.query(SubjectAreas.LangCode == 'en')
            units_en = q.fetch(999)

            for unit2 in units_en:
                if unit2.LearningUnitID not in countmap_other_language:
                    logging.info('QQQ: LearningUnitID to add in clone: %s' % unit2.LearningUnitID)
                    logging.info('QQQ: LangCode to add in clone: %s' % langCode)
                    n = SubjectAreas(LearningUnitID = unit2.LearningUnitID
                        , Name = unit2.Name
                        , LangCode = langCode
                        , Description = unit2.Description
                        , Status = 'Pending Translation'
                        )
                    n.put()
            return self.redirect('/subjareas')        

        else:
            return self.redirect('/subjareas')  