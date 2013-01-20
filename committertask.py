import webapp2
from google.appengine.api import taskqueue
from committer import Committer
from models import GeneratedFiles
from secrets import secret_botpassword
from google.appengine.ext import blobstore

class CommitterTask(webapp2.RequestHandler):
    """
    GET: Creates a task queue entry
    POST: Runs through all GeneratedFiles entries and creates a commit
    """

    def post(self):

        committer = Committer("SkGithubBot", secret_botpassword, "EduExport", "master")
        items = []

        langcode = self.request.get('langcode')
        all = GeneratedFiles.query(GeneratedFiles.LangCode == langcode).fetch()
        for generated in all:
            if not generated or not generated.blob:
                logger.error("GeneratedFiles %s does not have a blob, or could not be found." % identifier)
                return
            else:
                blobinfo = blobstore.BlobInfo.get(generated.blob) 
                reader = blobinfo.open()
                content = reader.read()
                path = ""
                try:
                    path = generated.LangCode + "/"  + generated.FileGenPath + "/" + generated.SearchName
                except TypeError:
                    path = generated.LangCode + "/NOPATH/"  + generated.SearchName
                path = path.replace("\\", "/")
                items.append({
                    "path": path,
                    "mode": "100644",
                    "content": content,
                })

        committer.commit(items)

    def get(self):
        langcode = self.request.get('langcode')
        taskqueue.add(url='/commit', params={'langcode': langcode})
