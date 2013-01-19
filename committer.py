from google.appengine.api import urlfetch
from base64 import encodestring as base64
import logging
try: 
    import simplejson as json
except ImportError: 
    import json

class Committer:
    """
    Github API interface for committing files.
    """

    def __init__ (self, username, password, repo, branch):
         self.username = username
         self.password = password
         self.repo = repo
         self.branch = branch
         self.auth = 'Basic %s' % base64('%s:%s' % (username, password)).replace('\n', '')
         self.baseurl = "https://api.github.com/repos/" + username + "/" + repo + "/git/"

    def commit(self, items):
        """
        @param items: Array of Hash objects, of path, mode, type and content specifying a tree structure.
                      item.path: String of the file referenced in the tree
                      item.mode: String of the file mode - one of 100644 for file (blob), 100755 for executable (blob), 040000 for subdirectory (tree), 160000 for submodule (commit) or 120000 for a blob that specifies the path of a symlink
                      item.content: String of content you want this file to have - GitHub will write this blob out and use that SHA for this entry. Use either this or tree.sha
        """
        commitSHA = self.getCommitSHA()
        treeSHA = self.getTreeSHA(commitSHA)
        tree = { "base_tree" : treeSHA, "tree": items }
        newtreeSHA = self.postTree(tree)
        newcommitSHA = self.postCommit(commitSHA, newtreeSHA)
        self.postReference(newcommitSHA)

	#GET /refs/heads/{branch}
    def getCommitSHA(self):
        url = self.baseurl + "refs/heads/" + self.branch
        result = urlfetch.fetch(url=url,
            headers={'Authorization' : self.auth})
        jsonresult = json.loads(result.content)
        logging.info(result.content)
        return jsonresult['object']['sha'];

    #GET /commits/{sha}
    def getTreeSHA(self, sha):
        url = self.baseurl + "commits/" + sha
        result = urlfetch.fetch(url=url,
            headers={'Authorization' : self.auth})
        jsonresult = json.loads(result.content)
        logging.info(result.content)
        return jsonresult['tree']['sha']

    #POST /trees
    def postTree(self, tree):
        url = self.baseurl + "trees"
        payload = json.dumps(tree)
        result = urlfetch.fetch(url=url,
                payload=payload,
                method=urlfetch.POST,
                headers={'Authorization' : self.auth})
        jsonresult = json.loads(result.content)
        logging.info(result.content)
        return jsonresult['sha']

    #POST /commits
    def postCommit(self, commitsha, newtreesha):
        url = self.baseurl + "commits"
        postdata = {
            "message" : "An SkGithubBot Commit",
            "parents" : [commitsha],
            "tree" : newtreesha
        }
        payload = json.dumps(postdata)
        result = urlfetch.fetch(url=url,
                payload=payload,
                method=urlfetch.POST,
                headers={'Authorization' : self.auth})
        logging.info(result.content)
        return json.loads(result.content)['sha']

    #POST /refs/head/{branch}
    def postReference(self, newcommitsha):
        url = self.baseurl + "refs/heads/" + self.branch
        postdata = {
            "sha" : newcommitsha
        }
        payload = json.dumps(postdata)
        result = urlfetch.fetch(url=url,
                payload=payload,
                method=urlfetch.POST,
                headers={'Authorization' : self.auth})
        logging.info(result.content)
