"""The module for handling users."""

from appengine_config import JINJA_ENVIRONMENT
from auth import oauth_decorator
from datastore import User
from error_handlers import Handle500
from google.appengine.api import app_identity
import webapp2


def _GenerateTokenPayload(users):
  """Generate the token payload data for all users and their public keys.
    I could just pass through all the user's properties here, but that
    would expose the private key we have in the datastore along with
    various other user data, so I'm explicitly limiting what we show to
    an email and public key pair along with the datastore key.

    Args:
      users: A list of users with associated properties from the datastore.

    Returns:
      user_token_payloads: A dictionary with user key id as key, and a token
          and email tuple as a value.
  """
  user_token_payloads = {}
  for user in users:
    tup1 = (user.email, user.public_key)
    user_token_payloads[user.key.urlsafe()] = tup1

  return user_token_payloads


def _GenerateUserPayload(users):
  """Generate the user payload data for all users.
    I could just pass through all the user's properties here, but that
    would expose the private key we have in the datastore along with
    various other user data, so I'm explicitly limiting what we show to
    an email and key for modifying values.

    Args:
      users: A list of users with associated properties from the datastore.

    Returns:
      user_token_payloads: A dictionary with user key id as key and email
          as a value.
  """
  user_token_payloads = {}
  for user in users:
    user_token_payloads[user.key.urlsafe()] = user.email

  return user_token_payloads


def _RenderUserListTemplate():
  """Render a list of users."""
  users = User.GetAll()
  user_payloads = _GenerateUserPayload(users)
  template_values = {
      'host': app_identity.get_default_version_hostname(),
      'user_payloads': user_payloads
  }
  template = JINJA_ENVIRONMENT.get_template('templates/user.html')
  return template.render(template_values)


def _RenderTokenListTemplate():
  """Render a list of users and their tokens."""
  users = User.GetAll()
  user_token_payloads = _GenerateTokenPayload(users)

  template_values = {
      'host': app_identity.get_default_version_hostname(),
      'user_token_payloads': user_token_payloads
  }
  template = JINJA_ENVIRONMENT.get_template('templates/token.html')
  return template.render(template_values)


class ListUsersHandler(webapp2.RequestHandler):

  @oauth_decorator.oauth_required
  def get(self):
    self.response.write(_RenderUserListTemplate())


class DeleteUserHandler(webapp2.RequestHandler):

  @oauth_decorator.oauth_required
  def get(self):
    url_key = self.request.get('key')
    User.Delete_By_Key(url_key)
    self.response.write(_RenderUserListTemplate())


class ListTokensHandler(webapp2.RequestHandler):

  @oauth_decorator.oauth_required
  def get(self):
    self.response.write(_RenderTokenListTemplate())


class GetNewTokenHandler(webapp2.RequestHandler):

  @oauth_decorator.oauth_required
  def get(self):
    url_key = self.request.get('key')
    User._UpdateKeyPair(url_key)

    self.response.write(_RenderTokenListTemplate())


app = webapp2.WSGIApplication([
    ('/', ListUsersHandler),
    ('/user/delete', DeleteUserHandler),
    ('/user/listTokens', ListTokensHandler),
    ('/user/getNewToken', GetNewTokenHandler),
    (oauth_decorator.callback_path, oauth_decorator.callback_handler()),
], debug=True)

# This is the only way to catch exceptions from the oauth decorators.
app.error_handlers[500] = Handle500
