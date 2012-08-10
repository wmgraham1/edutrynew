import cgi
import datetime
import urllib
import webapp2

from google.appengine.ext import db
from google.appengine.ext import ndb
from google.appengine.api import users

class Languages(db.Model):
  langCode = db.StringProperty()
  langCode3 = db.StringProperty()
  langName = db.StringProperty()
  CreatedBy = db.UserProperty(auto_current_user=True)
  CreatedDate = db.DateTimeProperty(auto_now_add=True)

class ListItems(db.Model):
  ListItemName = db.StringProperty(required=True)
  ListTypeCode = db.StringProperty()
  Description = db.StringProperty()
  CreatedBy = db.UserProperty(auto_current_user=True)
  CreatedDate = db.DateTimeProperty(auto_now_add=True)
  
class ListTypes(ndb.Model):
  ListTypeName = ndb.StringProperty()
  ListTypeCode = ndb.StringProperty()
  Description = ndb.StringProperty()
  CreatedBy = ndb.UserProperty(auto_current_user=True)
  CreatedDate = ndb.DateTimeProperty(auto_now_add=True)

class PageContents(db.Model):
  """Models an individual pagecontent block with page name, content, createdby and createddate."""
  TemplateName = db.StringProperty()
  TokenTag = db.StringProperty()
  LangCode = db.StringProperty()
  ContentText = db.TextProperty()
  CreatedBy = db.UserProperty(auto_current_user=True)
  CreatedDate = db.DateTimeProperty(auto_now_add=True)
  UpdatedBy = db.UserProperty()
  UpdatedDate = db.DateTimeProperty()
  Status = db.StringProperty()
  StatusBy = db.UserProperty(auto_current_user=True)
  StatusDate = db.DateTimeProperty(auto_now_add=True)
  
class Papers(ndb.Model):
  """Models an individual pagecontent block with page name, content, createdby and createddate."""
  Title = ndb.StringProperty()
  Category = ndb.StringProperty()
  Text = ndb.TextProperty()
  CreatedBy = ndb.UserProperty(auto_current_user=True)
  CreatedDate = ndb.DateTimeProperty(auto_now_add=True)
  UpdatedBy = ndb.UserProperty()
  UpdatedDate = ndb.DateTimeProperty()
  Status = ndb.StringProperty()
  StatusBy = ndb.UserProperty(auto_current_user=True)
  StatusDate = ndb.DateTimeProperty(auto_now_add=True)

class Comments(ndb.Model):
  """Models an individual pagecontent block with page name, content, createdby and createddate."""
  Title = ndb.StringProperty()
  RefObjType = ndb.StringProperty()
  RefObjID = ndb.StringProperty()
  CommentCode = ndb.StringProperty()
  IndentClass = ndb.IntegerProperty()
  Text = ndb.TextProperty()
  CreatedBy = ndb.UserProperty(auto_current_user=True)
  CreatedDate = ndb.DateTimeProperty(auto_now_add=True)
  UpdatedBy = ndb.UserProperty()
  UpdatedDate = ndb.DateTimeProperty()
  Status = ndb.StringProperty()
  StatusBy = ndb.UserProperty(auto_current_user=True)
  StatusDate = ndb.DateTimeProperty(auto_now_add=True)


class Notes(db.Model):
  author = db.StringProperty()
  text = db.TextProperty()
  priority = db.StringProperty()
  status = db.StringProperty()
  date = db.DateTimeProperty(auto_now_add=True)
  whichuser = db.UserProperty()

class Obj(db.Model):
  OID = db.IntegerProperty(long)
  ClassName = db.StringProperty()
  CreatedBy = db.UserProperty(auto_current_user=True)
  CreatedDate = db.DateTimeProperty(auto_now_add=True)
  UpdatedDate = db.DateTimeProperty(auto_now_add=True)
  UpdatedBy = db.UserProperty()
  Status = db.IntegerProperty()  
  StatusBy = db.UserProperty(auto_current_user=True)
  StatusDate = db.DateTimeProperty(auto_now_add=True)

class TemplateTypes(db.Model):
  Name = db.StringProperty()
  TypeCode = db.StringProperty()
  Description = db.StringProperty()
  CreatedBy = db.UserProperty(auto_current_user=True)
  CreatedDate = db.DateTimeProperty(auto_now_add=True)
  Status = db.StringProperty()
  StatusBy = db.UserProperty(auto_current_user=True)
  StatusDate = db.DateTimeProperty(auto_now_add=True)
  
class Templates(db.Model):
  Name = db.StringProperty(required=True)
  TemplateType = db.StringProperty()
  Description = db.StringProperty()
  FileName = db.StringProperty()
  CreatedBy = db.UserProperty(auto_current_user=True)
  CreatedDate = db.DateTimeProperty(auto_now_add=True)
  Status = db.StringProperty(default="Pending Translation")
  StatusBy = db.UserProperty(auto_current_user=True)
  StatusDate = db.DateTimeProperty(auto_now_add=True)
 
class TokenValues(db.Model):
  templateName = db.StringProperty()
  TypeCode = db.StringProperty()
  langCode = db.StringProperty()
  tknID = db.StringProperty()
  tknValue = db.StringProperty()
  date = db.DateTimeProperty(auto_now_add=True)
  whichuser = db.UserProperty()
  createdDate = db.DateTimeProperty(auto_now_add=True)
  createdBy = db.UserProperty(auto_current_user=True)
  updatedDate = db.DateTimeProperty()
  updatedBy = db.UserProperty()
  status = db.StringProperty()  
  statusDate = db.DateTimeProperty(auto_now_add=True)
  statusBy = db.UserProperty(auto_current_user=True)
  
  
#  We should use ndb but seems to have issues with jinja2
# class TokenValues(ndb.Model):
#   templateName = ndb.StringProperty()
#   langCode = ndb.StringProperty()
#   tknID = ndb.StringProperty()
#   tknValue = ndb.StringProperty()
#   date = ndb.DateTimeProperty(auto_now_add=True)
#   whichuser = ndb.UserProperty()

