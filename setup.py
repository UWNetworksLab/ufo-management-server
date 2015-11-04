"""The setup module for first-time initialization of the app."""

from appengine_config import JINJA_ENVIRONMENT
from auth import oauth_decorator
from datastore import User
from datastore import OAuth
from error_handlers import Handle500
from google_directory_service import GoogleDirectoryService
import webapp2
import xsrf
import admin


JINJA_ENVIRONMENT.globals['xsrf_token'] = xsrf.xsrf_token


def _RenderSetupOAuthClientTemplate():
  """Render a setup page with inputs for client id and secret."""
  template_values = {
      'host': 'localhost:9999',
      'client_id': 'Your client_id goes here',
      'client_secret': 'Your client_secret goes here',
      'xsrf_token': xsrf.xsrf_token(),
  }
  template = JINJA_ENVIRONMENT.get_template('templates/setup_client.html')
  return template.render(template_values)


def _RenderSetupUsersTemplate():
  """Render a setup page with an import users button."""
  template_values = {
      'host': 'localhost:9999',
      'xsrf_token': xsrf.xsrf_token(),
  }
  template = JINJA_ENVIRONMENT.get_template('templates/setup_user.html')
  return template.render(template_values)


class SetupOAuthClientHandler(webapp2.RequestHandler):
  """Setup a client in the datastore."""

  @admin.require_admin
  def get(self):
    self.response.write(_RenderSetupOAuthClientTemplate())

  @admin.require_admin
  @xsrf.xsrf_protect
  def post(self):
    client_id = self.request.get('client_id')
    client_secret = self.request.get('client_secret')
    OAuth.SetEntity(client_id, client_secret)
    OAuth.Flush()
    self.response.write(_RenderSetupUsersTemplate())


class SetupUsersHandler(webapp2.RequestHandler):
  """Setup users in the datastore."""

  @admin.require_admin
  @xsrf.xsrf_protect
  @oauth_decorator.oauth_required
  def post(self):
    OAuth.Flush()
    if User.GetCount() > 0:
      return self.response.write('Unable to setup because app is already'
                                 'initialized.')

    directory_service = GoogleDirectoryService(oauth_decorator)
    directory_users = directory_service.GetUsers()
    User.InsertUsers(directory_users)
    self.response.write('Setup completed.')


app = webapp2.WSGIApplication([
    ('/setup/oauthclient', SetupOAuthClientHandler),
    ('/setup/users', SetupUsersHandler),
    #(oauth_decorator.callback_path, oauth_decorator.callback_handler()),
], debug=True)

# This is the only way to catch exceptions from the oauth decorators.
app.error_handlers[500] = Handle500
