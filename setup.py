"""The setup module for first-time initialization of the app."""

from appengine_config import JINJA_ENVIRONMENT
from auth import oauth_decorator
from datastore import User
from datastore import OAuth
from error_handlers import Handle500
from google_directory_service import GoogleDirectoryService
import webapp2


def _RenderSetupClientTemplate():
  """Render a setup page with inputs for client id and secret."""
  template_values = {
      'host': 'localhost:9999',
      'client_id': 'Your client_id goes here',
      'client_secret': 'Your client_secret goes here'
  }
  template = JINJA_ENVIRONMENT.get_template('templates/setupClient.html')
  return template.render(template_values)


def _RenderSetupUsersTemplate():
  """Render a setup page with an import users button."""
  template_values = {
      'host': 'localhost:9999'
  }
  template = JINJA_ENVIRONMENT.get_template('templates/setupUser.html')
  return template.render(template_values)


class Setup(webapp2.RequestHandler):
  """Setup the server on first run."""

  def get(self):
    self.response.write(_RenderSetupClientTemplate())


class SetupClientHandler(webapp2.RequestHandler):
  """Setup a client in the datastore."""

  def get(self):
    client_id = self.request.get('client_id')
    client_secret = self.request.get('client_secret')
    OAuth.SetEntity(client_id, client_secret)
    OAuth.Flush()
    self.response.write(_RenderSetupUsersTemplate())


class SetupUsersHandler(webapp2.RequestHandler):
  """Setup users in the datastore."""

  @oauth_decorator.oauth_required
  def get(self):
    OAuth.Flush()
    if User.GetCount() > 0:
      return self.response.write('Unable to setup because app is already'
                                 'initialized.')

    directory_service = GoogleDirectoryService(oauth_decorator)
    directory_users = directory_service.GetUsers()
    User.InsertUsers(directory_users)
    self.response.write('Setup completed.')


app = webapp2.WSGIApplication([
    ('/setup', Setup),
    ('/setup/client', SetupClientHandler),
    ('/setup/users', SetupUsersHandler),
    #(oauth_decorator.callback_path, oauth_decorator.callback_handler()),
], debug=True)

# This is the only way to catch exceptions from the oauth decorators.
app.error_handlers[500] = Handle500
