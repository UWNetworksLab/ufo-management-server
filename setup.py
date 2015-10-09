"""The setup module for first-time initialization of the app."""

from auth import oauth_decorator
from datastore import User
from error_handlers import Handle500
from google_directory_service import GoogleDirectoryService
import webapp2


class Setup(webapp2.RequestHandler):
  """Setup the server on first run."""

  @oauth_decorator.oauth_required
  def get(self):
    if User.GetCount() > 0:
      return self.response.write('Unable to setup because app is already'
                                 'initialized.')

    directory_service = GoogleDirectoryService(oauth_decorator)
    directory_users = directory_service.GetUsers()
    User.InsertUsers(directory_users)
    self.response.write('Setup completed.')


app = webapp2.WSGIApplication([
    ('/setup', Setup),
    (oauth_decorator.callback_path, oauth_decorator.callback_handler()),
], debug=True)

# This is the only way to catch exceptions from the oauth decorators.
app.error_handlers[500] = Handle500
