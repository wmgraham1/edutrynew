import cgi
import datetime
import urllib
import webapp2

from google.appengine.ext import db
from google.appengine.ext import ndb
from google.appengine.api import users

class Languages(ndb.Model):
  langCode = ndb.StringProperty()
  langCode3 = ndb.StringProperty()
  langName = ndb.StringProperty()
  CreatedBy = ndb.UserProperty(auto_current_user_add=True)
  CreatedDate = ndb.DateTimeProperty(auto_now_add=True)

class PageContents(ndb.Model):
  """Models an individual pagecontent block with page name, content, createdby and createddate."""
  TemplateName = ndb.StringProperty()
  TokenTag = ndb.StringProperty()
  LangCode = ndb.StringProperty()
  ContentText = ndb.TextProperty()
  CreatedBy = ndb.UserProperty(auto_current_user_add=True)
  CreatedDate = ndb.DateTimeProperty(auto_now_add=True)
  UpdatedBy = ndb.UserProperty()
  UpdatedDate = ndb.DateTimeProperty()
  Status = ndb.StringProperty()
  StatusBy = ndb.UserProperty(auto_current_user_add=True)
  StatusDate = ndb.DateTimeProperty(auto_now_add=True)
  
class Papers(ndb.Model):
  """Models an individual pagecontent block with page name, content, createdby and createddate."""
  Title = ndb.StringProperty()
  Category = ndb.StringProperty()
  Text = ndb.TextProperty()
  CreatedBy = ndb.UserProperty(auto_current_user_add=True)
  CreatedDate = ndb.DateTimeProperty(auto_now_add=True)
  UpdatedBy = ndb.UserProperty()
  UpdatedDate = ndb.DateTimeProperty()
  Status = ndb.StringProperty()
  StatusBy = ndb.UserProperty(auto_current_user_add=True)
  StatusDate = ndb.DateTimeProperty(auto_now_add=True)

class Comments(ndb.Model):
  """Models an individual pagecontent block with page name, content, createdby and createddate."""
  Title = ndb.StringProperty()
  RefObjType = ndb.StringProperty()
  RefObjID = ndb.StringProperty()
  CommentCode = ndb.StringProperty()
  IndentClass = ndb.IntegerProperty()
  Text = ndb.TextProperty()
  CreatedBy = ndb.UserProperty(auto_current_user_add=True)
  CreatedDate = ndb.DateTimeProperty(auto_now_add=True)
  UpdatedBy = ndb.UserProperty()
  UpdatedDate = ndb.DateTimeProperty()
  Status = ndb.StringProperty()
  StatusBy = ndb.UserProperty(auto_current_user_add=True)
  StatusDate = ndb.DateTimeProperty(auto_now_add=True)


class Templates(ndb.Model):
  Name = ndb.StringProperty(required=True)
  FolderName = ndb.StringProperty()
  TemplateType = ndb.StringProperty()
  Description = ndb.StringProperty()
  FileName = ndb.StringProperty()
  CreatedBy = ndb.UserProperty(auto_current_user_add=True)
  CreatedDate = ndb.DateTimeProperty(auto_now_add=True)
  Status = ndb.StringProperty(default="Pending Translation")
  StatusBy = ndb.UserProperty(auto_current_user_add=True)
  StatusDate = ndb.DateTimeProperty(auto_now_add=True)
  UpdatedDate = ndb.DateTimeProperty()
  UpdatedBy = ndb.UserProperty()
 
class TokenValues(ndb.Model):
  templateName = ndb.StringProperty()
  TypeCode = ndb.StringProperty()
  langCode = ndb.StringProperty()
  tknID = ndb.StringProperty()
  tknValue = ndb.StringProperty()
  CreatedBy = ndb.UserProperty(auto_current_user=True)
  CreatedDate = ndb.DateTimeProperty(auto_now=True)
  Status = ndb.StringProperty(default="Pending Translation")
  StatusBy = ndb.UserProperty(auto_current_user_add=True)
  StatusDate = ndb.DateTimeProperty(auto_now_add=True)
  UpdatedDate = ndb.DateTimeProperty()
  UpdatedBy = ndb.UserProperty()

class UserSuppl(ndb.Model):
  UserID = ndb.UserProperty(auto_current_user_add=True)
  FirstName = ndb.StringProperty()
  LastName = ndb.StringProperty()
  Descr = ndb.StringProperty()
  Role = ndb.StringProperty()
  Email = ndb.StringProperty()
  Permissions = ndb.IntegerProperty(repeated=True)
  CreatedBy = ndb.UserProperty(auto_current_user_add=True)
  CreatedDate = ndb.DateTimeProperty(auto_now_add=True)
  UpdatedDate = ndb.DateTimeProperty()
  UpdatedBy = ndb.UserProperty()
  Status = ndb.StringProperty()  
  StatusDate = ndb.DateTimeProperty(auto_now_add=True)
  StatusBy = ndb.UserProperty(auto_current_user=True)
  
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
  CreatedBy = db.UserProperty(auto_current_user_add=True)
  CreatedDate = db.DateTimeProperty(auto_now_add=True)
  UpdatedDate = db.DateTimeProperty(auto_now_add=True)
  UpdatedBy = db.UserProperty()
  Status = db.IntegerProperty()  
  StatusBy = db.UserProperty(auto_current_user_add=True)
  StatusDate = db.DateTimeProperty(auto_now_add=True)

class TemplateTypes(db.Model):
  Name = db.StringProperty()
  TypeCode = db.StringProperty()
  Description = db.StringProperty()
  CreatedBy = db.UserProperty(auto_current_user_add=True)
  CreatedDate = db.DateTimeProperty(auto_now_add=True)
  Status = db.StringProperty()
  StatusBy = db.UserProperty(auto_current_user_add=True)
  StatusDate = db.DateTimeProperty(auto_now_add=True)
  
class ListItems(db.Model):
  ListItemName = db.StringProperty(required=True)
  ListTypeCode = db.StringProperty()
  Description = db.StringProperty()
  CreatedBy = db.UserProperty(auto_current_user_add=True)
  CreatedDate = db.DateTimeProperty(auto_now_add=True)
  
class ListTypes(ndb.Model):
  ListTypeName = ndb.StringProperty()
  ListTypeCode = ndb.StringProperty()
  Description = ndb.StringProperty()
  CreatedBy = ndb.UserProperty(auto_current_user_add=True)
  CreatedDate = ndb.DateTimeProperty(auto_now_add=True)

  
#  We should use ndb but seems to have issues with jinja2
# class TokenValues(ndb.Model):
#   templateName = ndb.StringProperty()
#   langCode = ndb.StringProperty()
#   tknID = ndb.StringProperty()
#   tknValue = ndb.StringProperty()
#   date = ndb.DateTimeProperty(auto_now_add=True)
#   whichuser = ndb.UserProperty()

