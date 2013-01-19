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

        committer = Committer("SkGithubBot", secret_botpassword, "TestRepo", "master")
        items = []

        all = GeneratedFiles.query().fetch()
        for generated in all:
            if not generated or not generated.blob:
                logger.error("GeneratedFiles %s does not have a blob, or could not be found." % identifier)
                return
            else:
                blobinfo = blobstore.BlobInfo.get(generated.blob) 
                reader = blobinfo.open()
                content = reader.read()
                # TODO(wgraham1):  add GeneratedFiles.FilePath property
                path = generated.LangCode + "/" + generated.SearchName
                items.append({
                    "path": path,
                    "mode": "100644",
                    "content": content,
                })

        committer.commit(items)

    def get(self):
        taskqueue.add(url='/commit')
