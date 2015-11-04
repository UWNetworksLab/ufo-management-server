"""The logout module to facilitate testing switching between admin users."""

from google.appengine.api import users
from auth import oauth_decorator
#from datastore import User
#from datastore import OAuth
from error_handlers import Handle500
#from google_directory_service import GoogleDirectoryService
import webapp2
#import admin



class LogoutHandler(webapp2.RequestHandler):
  """Logs the current user out."""

  @oauth_decorator.oauth_required
  def get(self):
    logout_url = users.create_logout_url(self.request.url)
    self.redirect(logout_url)


app = webapp2.WSGIApplication([
    ('/logout', LogoutHandler),
    (oauth_decorator.callback_path, oauth_decorator.callback_handler()),
], debug=True)

# This is the only way to catch exceptions from the oauth decorators.
app.error_handlers[500] = Handle500
