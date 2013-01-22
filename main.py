#!/usr/bin/env python
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import jinja2
import webapp2
import os
import logging
from google.appengine.ext import ndb
from wtforms.ext.appengine.ndb import model_form
from webapp2_extras import sessions
from google.appengine.ext.webapp.util import run_wsgi_app

#import homepage
import pageadmin
#import aboutpage
import contactpage

#import notes
#import views
from Home import DisplayHome, DisplayTransIntro
from views import MainPage, CreateNote, DeleteNote, EditNote
from PageContent import PageContentList, PageContentCreate, PageContentEdit, PageContentDelete
from Paper import PaperList, PaperDisplay, PaperCreate, PaperEdit, PaperDelete, FeedbackList, FeedbackCreate, FeedbackDisplay, FeedbackEdit
from Comment import CommentList, CommentCreate, CommentSubCreate, CommentEdit, CommentDelete
from User import UserList, UserCreate, UserJoin, UserEdit, UserDelete, UserRightsCalc, SingleUserRightsCalc, PermissionTest, UserApplicationThanks
from Token import TokenStep1Page, TokenList, TokenCreate, TokenEdit, TokenDelete, TokenClone, TokenFileGen, TokenFileView, TemplateTokenCreate, TokenStep1PageEx, TokenEditList, TokenEditListPost
from Language import LangList, LangCreate, LangEdit, LangDelete
from Template import TemplateList, TemplateCreate, TemplateEdit, TemplateDelete
from ListType import ListTypeList, ListTypeCreate, ListTypeEdit, ListTypeDelete
from Security import PermissionList, RoleList, RoleDisplay
from GenFile import *
from About import DisplayAboutSite, DisplayAboutUs, DisplayAboutKA
from SubjAreas import SubjAreaList, SubjAreaCreate, SubjAreaEdit, SubjAreaDelete, SubjAreaClone, SubjAreaEditList, SubjAreaEditListPost
from Subjects import LearnSubjList, LearnSubjCreate, LearnSubjEdit, LearnSubjDelete, LearnSubjClone, LearnSubjEditList, LearnSubjEditListPost
from TopicAreas import TopicAreaList, TopicAreaCreate, TopicAreaEdit, TopicAreaDelete, TopicAreaClone, TopicAreaEditList, TopicAreaEditListPost
from TopicGrps import TopicGrpList, TopicGrpCreate, TopicGrpEdit, TopicGrpDelete, TopicGrpClone, TopicGrpEditList, TopicGrpEditListPost
from Units import LearnUnitList, LearnUnitCreate, LearnUnitEdit, LearnUnitDelete, LearnUnitClone, LearnUnitEditList, LearnUnitEditListPost, LearnUnitGenList
from Aids import LearnAidList, LearnAidCreate, LearnAidEdit, LearnAidDelete, LearnAidClone, LearnAidEditList, LearnAidEditListPost
from How import HowIntro, HowTrans, HowTransTheory
from Test1 import Test1Get, TextFileRender
#from MyFileHandlers import FileDownloadHandler, FileUploadFormHandler, FileUploadHandler, FileInfoHandler
from committertask import CommitterTask


# Below code is what the original exercise included
#class MainHandler(webapp2.RequestHandler):
#    def get(self):
#        self.response.out.write('Hello brave new world!')
config = {}
config['webapp2_extras.sessions'] = {
    'secret_key': 'my-super-secret-key',
}

app = webapp2.WSGIApplication([
	('/commit', CommitterTask),
	('/', DisplayHome),
	('/home', DisplayHome),
	('/transintro', DisplayTransIntro),
	('/about/site', DisplayAboutSite),
	('/about/us', DisplayAboutUs),
	('/about/ka', DisplayAboutKA),
    ('/feedback', FeedbackList),
    ('/feedback/display', FeedbackDisplay),
    ('/feedback/create', FeedbackCreate),
    ('/feedback/edit/([\d]+)', FeedbackEdit),
#    ('/files', FileUploadFormHandler),
#    ('/files/upload', FileUploadHandler),
#    ('/files/fileinfo/([\d]+)', FileInfoHandler),
#    ('/files/dowload/([\d]+)', FileDownloadHandler),
    ('/users', UserList),
    ('/users/join', UserJoin), 
    ('/users/create', UserCreate), 
    ('/users/applthks', UserApplicationThanks), 
    ('/users/permissiontest', PermissionTest), 
    ('/users/edit/([\d]+)', UserEdit), 
    ('/users/delete/([\d]+)', UserDelete), 
    ('/users/calcrights/([\w]+)', UserRightsCalc), 
    ('/users/calcuser/([\w]+)', SingleUserRightsCalc), 
    ('/admin/permissions', PermissionList),
    ('/admin/roles', RoleList),
    ('/admin/roles/display/([\w]+)', RoleDisplay),
    ('/pagecontents', PageContentList),
    ('/pagecontents/create', PageContentCreate), 
    ('/pagecontents/edit/([\d]+)', PageContentEdit), 
    ('/pagecontents/delete/([\d]+)', PageContentDelete), 
    ('/papers/display/([\d]+)', PaperDisplay), 
    ('/papers/create/', PaperCreate), 
    ('/papers/edit/([\d]+)', PaperEdit),
    ('/papers/delete/([\d]+)', PaperDelete),
    ('/papers/([\w]+)', PaperList),
    ('/comments', CommentList),
    ('/comments/create/([\d]+)', CommentCreate), 
    ('/comments/addcomment/([\d]+)', CommentSubCreate), 
    ('/comments/edit/([\d]+)', CommentEdit), 
    ('/comments/delete/([\d]+)', CommentDelete), 
    ('/notes', MainPage),
    ('/notes/create', CreateNote), 
    ('/notes/edit/([\d]+)', EditNote),
    ('/notes/delete/([\d]+)', DeleteNote),
    ('/tokens-step1', TokenStep1Page),
    ('/tokens-step1ex', TokenStep1PageEx),
    ('/tokens', TokenList),
    ('/tokensedit', TokenEditList), 
    ('/tokenslisteditpost/([\d]+)', TokenEditListPost), 
    ('/tokens/create', TokenCreate), 
    ('/tokens/createt', TemplateTokenCreate), 
    ('/tokens/edit/([\d]+)', TokenEdit),
    ('/tokens/delete/([\d]+)', TokenDelete),
    ('/tokens/clone', TokenClone),
    ('/tokens/translate', TokenFileGen),
    ('/tokens/viewtranslated', TokenFileView),
    ('/listtypes', ListTypeList),
    ('/listtypes/create', ListTypeCreate), 
    ('/listtypes/edit/([\d]+)', ListTypeEdit),
    ('/listtypes/delete/([\d]+)', ListTypeDelete),
    ('/langs', LangList),
    ('/langs/create', LangCreate), 
    ('/langs/edit/([\d]+)', LangEdit),
    ('/langs/delete/([\d]+)', LangDelete),
    ('/templates', TemplateList),
    ('/templates/create', TemplateCreate), 
    ('/templates/edit/([\d]+)', TemplateEdit),
    ('/templates/delete/([\d]+)', TemplateDelete),
    ('/genfiles', GenFileList), 
    ('/export', GenFileExportList), 
    ('/genfilesinfolist', GenFileInfoList), 
    ('/genfiles/display/([\d]+)', GenFileDisplay),
    ('/genfiles/genfiledownload/([\d]+)', FileDownloadHandler),
    ('/genfiles/genfiletry/([\d]+)', FileTryHandler),
    ('/genfiles/try/utils/([\w]+)/(.+)', FileTryHandlerAltTry),
    ('/genfiles/try/([\w]+)/(.+)', FileTryHandlerAlt),
    ('/genfiles/try/khan-exercise.js', GenFileRedirect),
    ('/genfiles/try/utils/math-format.js', GenFileRedirectMathFormats),
    ('/genfiles/try/utils/hints.js', GenFileRedirectHints),
    ('/genfiles/try/utils/answer-types.js', GenFileRedirectAnswerTypes),
    ('/genfiles/try/utils/graphie-helpers-arithmetic.js', GenFileRedirectGraphieHelpersArithmetic),
    ('/genfiles/altdisplay', GenFileAltDisplay),
    ('/genfiles/delete/([\d]+)', GenFileDelete),
    ('/subjareasedit', SubjAreaEditList), 
    ('/subjareaseditpost/([\d]+)', SubjAreaEditListPost),
    ('/subjareas', SubjAreaList), 
    ('/subjareas/create', SubjAreaCreate), 
    ('/subjareas/edit/([\d]+)', SubjAreaEdit),
    ('/subjareas/clone', SubjAreaClone),
    ('/subjareas/delete/([\d]+)', SubjAreaDelete),
    ('/subjs', LearnSubjList), 
    ('/subjsedit', LearnSubjEditList), 
    ('/subjseditpost/([\d]+)', LearnSubjEditListPost), 
    ('/subjs/create', LearnSubjCreate), 
    ('/subjs/edit/([\d]+)', LearnSubjEdit),
    ('/subjs/clone', LearnSubjClone),
    ('/subjs/delete/([\d]+)', LearnSubjDelete),
    ('/topareas', TopicAreaList), 
    ('/topareasedit', TopicAreaEditList), 
    ('/topareaseditpost/([\d]+)', TopicAreaEditListPost), 
    ('/topareas/create', TopicAreaCreate), 
    ('/topareas/edit/([\d]+)', TopicAreaEdit),
    ('/topareas/clone', TopicAreaClone),
    ('/topareas/delete/([\d]+)', TopicAreaDelete),
    ('/topgrps', TopicGrpList), 
    ('/topgrpsedit', TopicGrpEditList), 
    ('/topgrpseditpost/([\d]+)', TopicGrpEditListPost), 
    ('/topgrps/create', TopicGrpCreate), 
    ('/topgrps/edit/([\d]+)', TopicGrpEdit),
    ('/topgrps/clone', TopicGrpClone),
    ('/topgrps/delete/([\d]+)', TopicGrpDelete),
    ('/units', LearnUnitList), 
    ('/unitsgen/([\w]+)', LearnUnitGenList), 
    ('/unitsedit', LearnUnitEditList), 
    ('/unitseditpost/([\d]+)', LearnUnitEditListPost), 
    ('/units/create', LearnUnitCreate), 
    ('/units/edit/([\d]+)', LearnUnitEdit),
    ('/units/clone', LearnUnitClone),
    ('/units/delete/([\d]+)', LearnUnitDelete),
    ('/aids', LearnAidList), 
    ('/aidsedit', LearnAidEditList), 
    ('/aidseditpost/([\d]+)', LearnAidEditListPost), 
    ('/aids/create', LearnAidCreate), 
    ('/aids/edit/([\d]+)', LearnAidEdit),
    ('/aids/clone', LearnAidClone),
    ('/aids/delete/([\d]+)', LearnAidDelete),
    ('/how', HowIntro),
    ('/how/trans', HowTrans),
    ('/how/transtheory', HowTransTheory),
    ('/test1', Test1Get),
    ('/textfilerender', TextFileRender)
	],
                config=config,
                debug=True)

def main():
    run_wsgi_app(app)

if __name__ == '__main__':
    main()
