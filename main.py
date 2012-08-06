#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
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
from google.appengine.ext.webapp.util import run_wsgi_app

import webapp2
import homepage
import pageadmin
import aboutpage
import contactpage

#import notes
#import views
from views import MainPage, CreateNote, DeleteNote, EditNote
from PageContent import PageContentList, PageContentCreate, PageContentEdit, PageContentDelete
from Paper import PaperList, PaperDisplay, PaperCreate, PaperEdit, PaperDelete
from Comment import CommentList, CommentDisplay, CommentCreate, CommentSubCreate, CommentEdit, CommentDelete
from Token import TokenStep1Page, TokenList, TokenCreate, TokenEdit, TokenDelete, TokenClone
from Language import LangList, LangCreate, LangEdit, LangDelete
from Template import TemplateList, TemplateCreate, TemplateEdit, TemplateDelete
from ListType import ListTypeList, ListTypeCreate, ListTypeEdit, ListTypeDelete


# Below code is what the original exercise included
#class MainHandler(webapp2.RequestHandler):
#    def get(self):
#        self.response.out.write('Hello brave new world!')
config = {}
config['webapp2_extras.sessions'] = {
    'secret_key': 'my-super-secret-key',
}

app = webapp2.WSGIApplication([
	('/', homepage.ViewHomePage),
	('/about', aboutpage.ViewAboutPage),
	('/content', pageadmin.ViewContentPage),
	('/contact', contactpage.ViewContactPage),
    ('/pagecontents', PageContentList),
    ('/pagecontents/create', PageContentCreate), 
    ('/pagecontents/edit/([\d]+)', PageContentEdit), 
    ('/pagecontents/delete/([\d]+)', PageContentDelete), 
    ('/papers', PaperList),
    ('/papers/display/([\d]+)', PaperDisplay), 
    ('/papers/create', PaperCreate), 
    ('/papers/edit/([\d]+)', PaperEdit),
    ('/papers/delete/([\d]+)', PaperDelete),
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
    ('/tokens', TokenList),
    ('/tokens/create', TokenCreate), 
    ('/tokens/edit/([\d]+)', TokenEdit),
    ('/tokens/delete/([\d]+)', TokenDelete),
    ('/tokens/clone', TokenClone),
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
    ('/templates/delete/([\d]+)', TemplateDelete)
	],
								config=config)
#							  debug=True)
		  


# below is the code that worked with Python (not 2.7)
#application = webapp2.WSGIApplication([
#	('/', homepage.ViewHomePage),
#	('/about', aboutpage.ViewAboutPage),
#	('/content', pageadmin.ViewContentPage)
#	],
#                              debug=True)
							  
#def main():
#    run_wsgi_app(application)

#if __name__ == '__main__':
#    main()