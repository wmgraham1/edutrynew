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
from DButils import TopicSeqRecalc, Test1


from models import KnowUnits
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

class Test1Get(BaseHandler):

    def get(self):
        languages = memcache.get("languages")
        if languages is not None:
            logging.info("get languages from memcache.")
        else:
            q = Languages.query().order(Languages.langName)
            languages = q.fetch(99)
            logging.info("Can not get languages from memcache.")
            if not memcache.add("languages", languages, 99):
                logging.info("Memcache set failed.")

        if self.request.get('langCode'):
            langCode=self.request.get('langCode')
            self.session['langCode'] = langCode
        else:
            langCode = self.session.get('langCode')
        if not langCode:
            self.session['langCode'] = 'en' 
            langCode = 'en'

        y = 'hi there'
        TestVal1 = '' + Test1(y)
        logging.info('GGG: Test if function calls: %s' % TestVal1)

        logout = None
        login = None
        currentuser = users.get_current_user()
        if currentuser:
              logout = users.create_logout_url('/subjs' )
        else:
              login = users.create_login_url('/subjs')
		  
        self.render_template('Test1.html', {'TestVal1':TestVal1, 'currentuser':currentuser, 'login':login, 'logout': logout})


class LearnSubjDelete(BaseHandler):

    def get(self, unit_id):
        iden = int(unit_id)
        unit = ndb.Key('Subjects', iden).get()
        currentuser = users.get_current_user()
#        if currentuser != template.CreatedBy and not users.is_current_user_admin():
#            self.abort(403)
#            return
        unit.key.delete()
        return self.redirect('/subjs')

class LearnSubjClone(BaseHandler):

    def get(self):
        if self.request.get('langCode'):
            langCode = self.request.get('langCode')

            q = Subjects.query(Subjects.LangCode == langCode)
            units = q.fetch(999)

            countmap_other_language={}
            for unit in units:
                logging.info('QQQ: LangCode in clone: %s' % unit.LangCode)
                if unit.LearningUnitID not in countmap_other_language:
                    logging.info('QQQ: LearningUnitID in clone: %s' % unit.LearningUnitID)
                    countmap_other_language[unit.LearningUnitID] = 1

            q = Subjects.query(Subjects.LangCode == 'en')
            units_en = q.fetch(999)

            for unit2 in units_en:
                if unit2.LearningUnitID not in countmap_other_language:
                    logging.info('QQQ: LearningUnitID to add in clone: %s' % unit2.LearningUnitID)
                    logging.info('QQQ: LangCode to add in clone: %s' % langCode)
                    n = Subjects(LearningUnitID = unit2.LearningUnitID
                        , Subject = unit2.Subject
                        , Name = unit2.Name
                        , LangCode = langCode
                        , Description = unit2.Description
                        , Status = 'Pending Translation'
                        )
                    n.put()
            return self.redirect('/subjs')        

        else:
            return self.redirect('/subjs')  