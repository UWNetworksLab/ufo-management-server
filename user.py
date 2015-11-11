"""The module for handling users."""

from appengine_config import JINJA_ENVIRONMENT
from auth import oauth_decorator
from datastore import User
from error_handlers import Handle500
from google.appengine.api import app_identity
import webapp2


def _RenderUserListTemplate():
  """Render a list of users."""
  users = User.GetAll()
  template_values = {
      'host': app_identity.get_default_version_hostname(),
      'users': users
  }
  template = JINJA_ENVIRONMENT.get_template('templates/user.html')
  return template.render(template_values)


class ListUsersHandler(webapp2.RequestHandler):

  @oauth_decorator.oauth_required
  def get(self):
    self.response.write(_RenderUserListTemplate())


class DeleteUserHandler(webapp2.RequestHandler):

  @oauth_decorator.oauth_required
  def get(self):
    email = self.request.get('email')
    User.DeleteUser(email)
    self.response.write(_RenderUserListTemplate())


app = webapp2.WSGIApplication([
    ('/', ListUsersHandler),
    ('/user/delete', DeleteUserHandler),
    (oauth_decorator.callback_path, oauth_decorator.callback_handler()),
], debug=True)

# This is the only way to catch exceptions from the oauth decorators.
app.error_handlers[500] = Handle500
