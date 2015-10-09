"""The module for handling access tokens.

Can not name this token.py because it will collide with the oauth client
library.
"""

from appengine_config import JINJA_ENVIRONMENT
from auth import oauth_decorator
import base64
from Crypto.PublicKey import RSA
from datastore import Token
from datastore import User
from error_handlers import Handle500
from google.appengine.api import app_identity
import os
import webapp2


def _GenerateKeyPair():
  """Generate a private and public key pair in base64.

  Returns:
    key_pair: A dictionary with private_key and public_key in b64 value.
  """
  rsa_key = RSA.generate(2048)
  private_key = base64.urlsafe_b64encode(rsa_key.exportKey())
  public_key = base64.urlsafe_b64encode(rsa_key.publickey().exportKey())

  key_pair = {
    'private_key': private_key,
    'public_key': public_key
  }

  return key_pair


def _IsAuthorized(email, public_key):
  """Whether the public key is authorized to access the proxy service.

  Returns:
    boolean: True if authorized, False if not.
  """
  user, token = Token.GetToken(email, public_key)

  if user is None or token is None:
    return False

  # TODO(henryc): Change this to validate by signing an actual message
  # with private/public key if management server will really need to do this.
  if user.email == email and token.public_key == public_key:
    return True

  return False


def GetAllUserTokens():
  """Get all users and their tokens.

  Returns:
    user_tokens: A dictionary with email as key, and a list
        of their tokens as values.
  """
  user_tokens = {}
  users = User.GetUsers()
  for user in users:
    user_tokens[user.email] = Token.GetTokens(user.email)

  return user_tokens


def _RenderTokenListTemplate():
  """Render a list of users and their tokens."""
  user_tokens = GetAllUserTokens()
  template_values = {
      'host': app_identity.get_default_version_hostname(),
      'user_tokens': user_tokens
  }
  template = JINJA_ENVIRONMENT.get_template('templates/token.html')
  return template.render(template_values)


class ListTokensHandler(webapp2.RequestHandler):

  @oauth_decorator.oauth_required
  def get(self):
    self.response.write(_RenderTokenListTemplate())


class AddTokenHandler(webapp2.RequestHandler):

  @oauth_decorator.oauth_required
  def get(self):
    email = self.request.get('email')
    Token.InsertToken(email, _GenerateKeyPair())

    self.response.write(_RenderTokenListTemplate())


class DeleteTokenHandler(webapp2.RequestHandler):

  @oauth_decorator.oauth_required
  def get(self):
    email = self.request.get('email')
    public_key = self.request.get('public_key')
    Token.DeleteToken(email, public_key)

    self.response.write(_RenderTokenListTemplate())


class AuthorizeTokenHandler(webapp2.RequestHandler):

  @oauth_decorator.oauth_required
  def get(self):
    email = self.request.get('email')
    b64_public_key = self.request.get('public_key')
    is_authorized = _IsAuthorized(email, b64_public_key)

    html = ('<html><body>'
            'email: %s<br />'
            'public_key: %s<br />'
            'is_authorized: %s'
            '</body></html>')
    self.response.write(html % (email, b64_public_key, is_authorized))


app = webapp2.WSGIApplication([
    ('/token/add', AddTokenHandler),
    ('/token/authorize', AuthorizeTokenHandler),
    ('/token/delete', DeleteTokenHandler),
    ('/token/list', ListTokensHandler),
    (oauth_decorator.callback_path, oauth_decorator.callback_handler()),
], debug=True)

app.error_handlers[500] = Handle500
