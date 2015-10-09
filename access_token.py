"""The module for handling access tokens.

Can not name this token.py because it will collide with the oauth client
library.
"""

from appengine_config import JINJA_ENVIRONMENT
from auth import oauth_decorator
import base64
import binascii
from Crypto.PublicKey import RSA
from datastore import Token
from datastore import User
from error_handlers import Handle500
from google.appengine.api import app_identity
import json
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


def _GenerateTokenPayload(user_tokens):
  """Generate the token payload data for all users and their public keys.

    Args:
      user_tokens: A dictionary with email as key, and a list
          of their tokens as values.

    Returns:
      user_token_payloads: A dictionary with email as key, and a list
          of their token payloads as values.
  """
  user_token_payloads = {}
  for email, tokens in user_tokens.iteritems():
    token_payloads = []
    for token in tokens:
      data = {}
      data['email'] = email
      data['public_key'] = token.public_key
      json_data = json.dumps(data)
      b64_data = binascii.b2a_base64(json_data)
      token_payloads.append(b64_data)
    user_token_payloads[email] = token_payloads

  return user_token_payloads


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
  user_token_payloads = _GenerateTokenPayload(user_tokens)

  template_values = {
      'host': app_identity.get_default_version_hostname(),
      'user_token_payloads': user_token_payloads
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
    token_payload = self.request.get('payload')
    json_data = json.loads(binascii.a2b_base64(token_payload))
    Token.DeleteToken(json_data['email'], json_data['public_key'])

    self.response.write(_RenderTokenListTemplate())


class AuthorizeTokenHandler(webapp2.RequestHandler):

  @oauth_decorator.oauth_required
  def get(self):
    token_payload = self.request.get('payload')
    json_data = json.loads(binascii.a2b_base64(token_payload))
    is_authorized = _IsAuthorized(json_data['email'], json_data['public_key'])

    html = ('<html><body>'
            'email: %s<br />'
            'public_key: %s<br />'
            'is_authorized: %s'
            '</body></html>')
    self.response.write(html % (json_data['email'],
                                json_data['public_key'],
                                is_authorized))


app = webapp2.WSGIApplication([
    ('/token/add', AddTokenHandler),
    ('/token/authorize', AuthorizeTokenHandler),
    ('/token/delete', DeleteTokenHandler),
    ('/token/list', ListTokensHandler),
    (oauth_decorator.callback_path, oauth_decorator.callback_handler()),
], debug=True)

app.error_handlers[500] = Handle500
