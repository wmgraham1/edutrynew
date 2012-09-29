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

def TopicSeqRecalc():
    dic_en = {}
    q2 = Subjects.query(Subjects.LangCode == 'en')
    unitsen = q2.fetch(999)
    for uniten in unitsen:
        logging.info('GGG: TopicSeqRecalc / Seq before: %d' % uniten.Seq)
        seq = uniten.Seq
        if seq == None:
            seq = 256
        logging.info('GGG: TopicSeqRecalc / Adding Subjects to Dic: %s' % uniten.LearningUnitID)
        logging.info('GGG: TopicSeqRecalc / Adding Seq to Dic: %d' % seq)
        dic_en[uniten.LearningUnitID] = seq

    q = Subjects.query(Subjects.LangCode != 'en')
    units = q.fetch(999)
    for unit in units:
        logging.info('GGG: TopicSeqRecalc / Updating Subjects %s' % unit.LearningUnitID)
        logging.info('GGG: TopicSeqRecalc / Updating Subjects Seq: %d' % dic_en[unit.LearningUnitID])
        unit.Seq = dic_en[unit.LearningUnitID]
        unit.put()

    return  

def UnitSeqRecalc():
    dic_en = {}
    q2 = LearningUnits.query(LearningUnits.LangCode == 'en')
    unitsen = q2.fetch(999)
    for uniten in unitsen:
        logging.info('GGG: TopicSeqRecalc / Seq before: %d' % uniten.Seq)
        seq = uniten.Seq
        if seq == None:
            seq = 999
        logging.info('GGG: TopicSeqRecalc / Adding Subjects to Dic: %s' % uniten.LearningUnitID)
        logging.info('GGG: TopicSeqRecalc / Adding Seq to Dic: %d' % seq)
        dic_en[uniten.LearningUnitID] = seq

    q = LearningUnits.query(LearningUnits.LangCode != 'en')
    units = q.fetch(999)
    for unit in units:
        logging.info('GGG: TopicSeqRecalc / Updating Subjects %s' % unit.LearningUnitID)
        logging.info('GGG: TopicSeqRecalc / Updating Subjects Seq: %d' % dic_en[unit.LearningUnitID])
        unit.Seq = dic_en[unit.LearningUnitID]
        unit.put()

    return  

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

def Test1(LangCode):
    if LangCode:
        self.session['LangCode'] = LangCode
    else:
        LangCode = self.session.get('LangCode')
    if not LangCode:
        self.session['LangCode'] = 'en' 
        LangCode = 'en'
    return LangCode
    
def FileBlobKeyGet(LangCode, SearchName):
    q = GeneratedFiles.query(GeneratedFiles.LangCode == LangCode, GeneratedFiles.SearchName == SearchName)
    genfile = q.get()
#    if genfile:
    return genfile.blob
#    else:
#        return ???
    
    
def loader(x):
    if x == 'test1.html':
        r = '{% extends "section.html" %}{% block content %}<br /><br /><p>The first test value starts here {{val1}}.  And {{val2}} is the 2nd test value.</p>{% endblock content %}'
    elif x == 'section.html':
        r = '{% extends "page_template1.html" %}{% block content %}<p>some more</p>{% endblock content %}'
    elif x == 'page_template1.html':
        r = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd"><body><p>the internal content will follow</p> <div id="contentColumn"><div class="wrapper">{% block content %} {% endblock content %}</div></div><p>the internal content preceeds here.</p> </body></html>'
    return r
