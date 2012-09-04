import jinja2
import os
import webapp2
import logging
from datetime import datetime
from google.appengine.ext import db
from google.appengine.ext import ndb
from google.appengine.api import users
from SecurityUtils import AccessOK

from models import UserSuppl

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

class PermissionList(BaseHandler):

    def get(self):
        PermissionDict = {}
        PermissionDict[1] = 'Permission to purely administrative functions.'
        PermissionDict[110] = 'Permission to View Papers and Discussion Topics.'
        PermissionDict[111] = 'Permission to Create/Edit Papers and Discussion Topics.'
        PermissionDict[120] = 'Permission to View Comments on Papers and Discussion Topics.'
        PermissionDict[121] = 'Permission to Create/Edit Comments on Papers and Discussion Topics.'
        PermissionDict[210] = 'Permission to View Templates.'
        PermissionDict[211] = 'Permission to Create/Edit Templates.'
        PermissionDict[220] = 'Permission to View English Tokens.'
        PermissionDict[221] = 'Permission to Create/Edit English Tokens.'
        PermissionDict[230] = 'Permission to View Foreign Language Tokens.'
        PermissionDict[231] = 'Permission to Clone Foreign Language Tokens.'
        PermissionDict[232] = 'Permission to Translate/Edit Foreign Language Tokens.'
#        RoleDict = ['admin', 'tokenbuilder', 'tokenbuilder_lmtd', 'advocate', 'volunteer', 'participant'];
#        RoleList = ['admin', 'tokenbuilder', 'tokenbuilder_lmtd', 'exercise'];	
        RoleDict = {}	
        RoleDict['admin'] = 'Has access to everything.'
        RoleDict['tokenbuilder'] = 'Can create Templates and English Tokens plus the permissions of Token-Translator.'
        RoleDict['tokentranslator'] = 'Can create Tokens in any language except English.'
        RoleDict['advocate'] = 'Advocates can create papers and post initial discussion topics.'
        RoleListAdvocate = [110, 111, 120, 121, 210, 220, 230, 231, 232];
        RoleListTokenBuilder = [110, 111, 120, 121, 210, 220, 230, 231, 232];
        RoleListTokenTranslator = [110,111,120, 121, 210, 220, 230, 231, 232];
        RolePermissionDict = {}
        RolePermissionDict['advocate'] = RoleListAdvocate
        RolePermissionDict['tokenbuilder'] = RoleListTokenBuilder
        RolePermissionDict['tokentranslator'] = RoleListTokenTranslator

        logout = None
        login = None
        currentuser = users.get_current_user()
#        if currentuser:
#              logout = users.create_logout_url('/templates' )
#        else:
#              login = users.create_login_url('/templates/create')
#        self.render_template('PermissionList.html', {'PermissionDict': PermissionDict, 'currentuser':currentuser, 'login':login, 'logout': logout})
        self.render_template('PermissionList.html', {'PermissionDict': PermissionDict})


class RoleList(BaseHandler):

    def get(self):
        PermissionDict = {}
        PermissionDict[1] = 'Permission to purely administrative functions.'
        PermissionDict[110] = 'Permission to View Papers and Discussion Topics.'
        PermissionDict[111] = 'Permission to Create/Edit Papers and Discussion Topics.'
        PermissionDict[120] = 'Permission to View Comments on Papers and Discussion Topics.'
        PermissionDict[121] = 'Permission to Create/Edit Comments on Papers and Discussion Topics.'
        PermissionDict[210] = 'Permission to View Templates.'
        PermissionDict[211] = 'Permission to Create/Edit Templates.'
        PermissionDict[220] = 'Permission to View English Tokens.'
        PermissionDict[221] = 'Permission to Create/Edit English Tokens.'
        PermissionDict[230] = 'Permission to View Foreign Language Tokens.'
        PermissionDict[231] = 'Permission to Clone Foreign Language Tokens.'
        PermissionDict[232] = 'Permission to Translate/Edit Foreign Language Tokens.'
#        RoleDict = ['admin', 'tokenbuilder', 'tokenbuilder_lmtd', 'advocate', 'volunteer', 'participant'];
#        RoleList = ['admin', 'tokenbuilder', 'tokenbuilder_lmtd', 'exercise'];	
        RoleDict = {}	
        RoleDict['admin'] = 'Has access to everything.'
        RoleDict['tokenbuilder'] = 'Can create Templates and English Tokens plus the permissions of Token-Translator.'
        RoleDict['tokentranslator'] = 'Can create Tokens in any language except English.'
        RoleDict['advocate'] = 'Advocates can create papers and post initial discussion topics.'
        RoleListAdvocate = [110, 111, 120, 121, 210, 220, 230, 231, 232];
        RoleListTokenBuilder = [110, 111, 120, 121, 210, 220, 230, 231, 232];
        RoleListTokenTranslator = [110,111,120, 121, 210, 220, 230, 231, 232];
        RolePermissionDict = {}
        RolePermissionDict['advocate'] = RoleListAdvocate
        RolePermissionDict['tokenbuilder'] = RoleListTokenBuilder
        RolePermissionDict['tokentranslator'] = RoleListTokenTranslator

        logout = None
        login = None
        currentuser = users.get_current_user()
#        if currentuser:
#              logout = users.create_logout_url('/templates' )
#        else:
#              login = users.create_login_url('/templates/create')
#        self.render_template('PermissionList.html', {'PermissionDict': PermissionDict, 'currentuser':currentuser, 'login':login, 'logout': logout})
        self.render_template('RoleList.html', {'RoleDict': RoleDict})	
		
	


class RoleDisplay(BaseHandler):

    def get(self, role_key):
        PermissionDict = {}
        PermissionDict[1] = 'Permission to purely administrative functions.'
        PermissionDict[110] = 'Permission to View Papers and Discussion Topics.'
        PermissionDict[111] = 'Permission to Create/Edit Papers and Discussion Topics.'
        PermissionDict[120] = 'Permission to View Comments on Papers and Discussion Topics.'
        PermissionDict[121] = 'Permission to Create/Edit Comments on Papers and Discussion Topics.'
        PermissionDict[210] = 'Permission to View Templates.'
        PermissionDict[211] = 'Permission to Create/Edit Templates.'
        PermissionDict[220] = 'Permission to View English Tokens.'
        PermissionDict[221] = 'Permission to Create/Edit English Tokens.'
        PermissionDict[230] = 'Permission to View Foreign Language Tokens.'
        PermissionDict[231] = 'Permission to Clone Foreign Language Tokens.'
        PermissionDict[232] = 'Permission to Translate/Edit Foreign Language Tokens.'
#        RoleDict = ['admin', 'tokenbuilder', 'tokenbuilder_lmtd', 'advocate', 'volunteer', 'participant'];
#        RoleList = ['admin', 'tokenbuilder', 'tokenbuilder_lmtd', 'exercise'];	
        RoleDict = {}	
        RoleDict['admin'] = 'Has access to everything.'
        RoleDict['tokenbuilder'] = 'Can create Templates and English Tokens plus the permissions of Token-Translator.'
        RoleDict['tokentranslator'] = 'Can create Tokens in any language except English.'
        RoleDict['advocate'] = 'Advocates can create papers and post initial discussion topics.'
        RoleListAdvocate = [110, 111, 120, 121, 210, 220, 230, 231, 232];
        RoleListTokenBuilder = [110, 111, 120, 121, 210, 220, 230, 231, 232];
        RoleListTokenTranslator = [110,111,120, 121, 210, 220, 230, 231, 232];
        RolePermissionDict = {}
        RolePermissionDict['advocate'] = RoleListAdvocate
        RolePermissionDict['tokenbuilder'] = RoleListTokenBuilder
        RolePermissionDict['tokentranslator'] = RoleListTokenTranslator

        #TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'templates')
        jinja_environment = \
            jinja2.Environment(autoescape=False, loader=jinja2.FileSystemLoader(TEMPLATE_DIR))

#        template = jinja_environment.get_template('RDisplay.html')
#        self.response.out.write(template.render(template_values))

        RolePermissionDictYes = {}
        RolePermissionDictNo = {}
        RolePermissionList = RolePermissionDict[role_key]
        logging.info('QQQ: RolePermissionList: %s' % RolePermissionList[0:len(RolePermissionList)])

        for key, value in PermissionDict.items():
            if key in RolePermissionList:
                RolePermissionDictYes[key] = value
            else:
                RolePermissionDictNo[key] = value

        logout = None
        login = None
        currentuser = users.get_current_user()
#        if currentuser:
#              logout = users.create_logout_url('/templates' )
#        else:
#              login = users.create_login_url('/templates/create')
#        self.render_template('PermissionList.html', {'PermissionDict': PermissionDict, 'currentuser':currentuser, 'login':login, 'logout': logout})
#        self.render_template('RoleDisplay.html', {'Role': role_key, 'RolePermissionList': RolePermissionList})	
        self.render_template('RoleDisplay.html', {'Role': role_key, 'RolePermissionDictYes': RolePermissionDictYes, 'RolePermissionDictNo': RolePermissionDictNo})	
		

def UserPermissionsCalc():
	PermissionDict = {}
	PermissionDict[1] = 'Permission to purely administrative functions.'
	PermissionDict[110] = 'Permission to View Papers and Discussion Topics.'
	PermissionDict[111] = 'Permission to Create/Edit Papers and Discussion Topics.'
	PermissionDict[120] = 'Permission to View Comments on Papers and Discussion Topics.'
	PermissionDict[121] = 'Permission to Create/Edit Comments on Papers and Discussion Topics.'
	PermissionDict[210] = 'Permission to View Templates.'
	PermissionDict[211] = 'Permission to Create/Edit Templates.'
	PermissionDict[220] = 'Permission to View Tokens.'
	PermissionDict[221] = 'Permission to Create/Edit English Tokens.'
	PermissionDict[230] = 'Permission to View Foreign Language Tokens.'
	PermissionDict[231] = 'Permission to Clone Foreign Language Tokens.'
	PermissionDict[232] = 'Permission to Translate/Edit Foreign Language Tokens.'
	RoleDict = {}	
	RoleDict['admin'] = 'Has access to everything.'
	RoleDict['tokenbuilder'] = 'Can create Templates and English Tokens plus the permissions of Token-Translator.'
	RoleDict['tokentranslator'] = 'Can create Tokens in any language except English.'
	RoleDict['advocate'] = 'Advocates can create papers and post initial discussion topics.'
	RoleListAdvocate = [110, 111, 120, 121, 210, 220, 230, 231, 232];
	RoleListTokenBuilder = [110, 111, 120, 121, 210, 220, 230, 231, 232];
	RoleListTokenTranslator = [110, 111, 120, 121, 210, 220, 230, 231, 232];
	RolePermissionDict = {}
	RolePermissionDict['advocate'] = RoleListAdvocate
	RolePermissionDict['tokenbuilder'] = RoleListTokenBuilder
	RolePermissionDict['tokentranslator'] = RoleListTokenTranslator

	#TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'templates')
	jinja_environment = \
		jinja2.Environment(autoescape=False, loader=jinja2.FileSystemLoader(TEMPLATE_DIR))

#        template = jinja_environment.get_template('RDisplay.html')
#        self.response.out.write(template.render(template_values))

	RolePermissionDictYes = {}
	RolePermissionDictNo = {}
	RolePermissionList = RolePermissionDict[role_key]
	logging.info('QQQ: RolePermissionList: %s' % RolePermissionList[0:len(RolePermissionList)])

	for key, value in PermissionDict.items():
		if key in RolePermissionList:
			RolePermissionDictYes[key] = value
		else:
			RolePermissionDictNo[key] = value

	q = UserSuppl.query()
	usersuppl = q.fetch(999)
# this function does not appear to have been completed.
	return
