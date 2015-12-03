"""The module for handling users."""

from appengine_config import JINJA_ENVIRONMENT
from auth import OAUTH_DECORATOR
import base64
from datastore import User
from datastore import DomainVerification
from datastore import ProxyServer
from error_handlers import Handle500
from google.appengine.api import app_identity
from google_directory_service import GoogleDirectoryService
import json
import random
import webapp2
import xsrf
import admin


JINJA_ENVIRONMENT.globals['xsrf_token'] = xsrf.xsrf_token()


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


def _MakeInviteCode(user):
  """Create an invite code for the given user.

  The invite code is a format created by the uproxy team. It includes the host
  ip (of the proxy server or load balancer) to connect the user to, the user
  username (user's email) to connect with, and the credential (private key)
  necessary to authenticate with the host.

    Args:
      user: A user from the datastore to generate an invite code for.

    Returns:
      invite_code: A base64 encoded dictionary of host, user, and pass which
      correspond to the proxy server/load balancer's ip, the user's email, and
      the user's private key, respectively.
  """
  invite_code_dictionary = {}
  invite_code_dictionary['host'] = _GetInviteCodeIp()
  invite_code_dictionary['user'] = user.email
  invite_code_dictionary['pass'] = user.private_key
  json_data = json.dumps(invite_code_dictionary)
  invite_code = base64.urlsafe_b64encode(json_data)

  return invite_code


def _GetInviteCodeIp():
  """Gets the ip address for placing in the invite code.

  Eventually this method will actually get the load balancer's ip as we will
  want in the final version. For now, it is used as a simple stub to just pick
  a random proxy server's ip.

    Returns:
      ip_address: An ip address for an invite code.
  """
  proxy_servers = ProxyServer.GetAll()
  index = random.randint(0, len(proxy_servers) - 1)
  return proxy_servers[index].ip_address


def _RenderUserListTemplate(invite_code=None):
  """Render a list of users."""
  users = User.GetAll()
  user_payloads = _GenerateUserPayload(users)
  template_values = {
      'host': app_identity.get_default_version_hostname(),
      'user_payloads': user_payloads
  }
  if invite_code is not None:
    template_values['invite_code'] = invite_code
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


def _RenderLandingTemplate():
  """Render the default landing page."""
  template_values = {
      'host': app_identity.get_default_version_hostname(),
      'site_verification_content': DomainVerification.GetOrInsertDefault().content,
  }
  template = JINJA_ENVIRONMENT.get_template('templates/landing.html')
  return template.render(template_values)


def _RenderAddUsersTemplate(directory_users):
  """Render a user add page that lets users be added by group key."""
  template_values = {
      'host': app_identity.get_default_version_hostname(),
      'directory_users': directory_users,
  }
  template = JINJA_ENVIRONMENT.get_template('templates/add_user.html')
  return template.render(template_values)


class LandingPageHandler(webapp2.RequestHandler):

  def get(self):
    self.response.write(_RenderLandingTemplate())


class ListUsersHandler(webapp2.RequestHandler):

  @OAUTH_DECORATOR.oauth_required
  def get(self):
    self.response.write(_RenderUserListTemplate())


class DeleteUserHandler(webapp2.RequestHandler):

  @OAUTH_DECORATOR.oauth_required
  def get(self):
    url_key = self.request.get('key')
    User.DeleteByKey(url_key)
    self.response.write(_RenderUserListTemplate())


class ListTokensHandler(webapp2.RequestHandler):

  @OAUTH_DECORATOR.oauth_required
  def get(self):
    self.response.write(_RenderTokenListTemplate())


class GetInviteCodeHandler(webapp2.RequestHandler):

  @OAUTH_DECORATOR.oauth_required
  def get(self):
    url_key = self.request.get('key')
    user = User.GetByKey(url_key)
    invite_code = _MakeInviteCode(user)

    self.response.write(_RenderUserListTemplate(invite_code))


class GetNewTokenHandler(webapp2.RequestHandler):

  @OAUTH_DECORATOR.oauth_required
  def get(self):
    url_key = self.request.get('key')
    User.UpdateKeyPair(url_key)

    self.response.write(_RenderTokenListTemplate())


class AddUsersHandler(webapp2.RequestHandler):
  """Add users into the datastore."""

  @admin.require_admin
  @OAUTH_DECORATOR.oauth_required
  def get(self):
    get_all = self.request.get('get_all')
    group_key = self.request.get('group_key')
    if get_all:
      directory_service = GoogleDirectoryService(OAUTH_DECORATOR)
      directory_users = directory_service.GetUsers()
      self.response.write(_RenderAddUsersTemplate(directory_users))
    elif group_key is not None and group_key is not '':
      directory_service = GoogleDirectoryService(OAUTH_DECORATOR)
      directory_users = directory_service.GetUsersByGroupKey(group_key)
      fixed_users = []
      for user in directory_users:
        user['primaryEmail'] = user['email']
        fixed_users.append(user)
      self.response.write(_RenderAddUsersTemplate(fixed_users))
    else:
      self.response.write(_RenderAddUsersTemplate([]))

  @admin.require_admin
  @xsrf.xsrf_protect
  @OAUTH_DECORATOR.oauth_required
  def post(self):
    params = self.request.get_all('selected_user')
    users = []
    for param in params:
      user = {}
      user['primaryEmail'] = param
      user['name'] = {}
      user['name']['fullName'] = param
      users.append(user)
    User.InsertUsers(users)
    self.redirect('/user')


app = webapp2.WSGIApplication([
    ('/', LandingPageHandler),
    ('/user', ListUsersHandler),
    ('/user/delete', DeleteUserHandler),
    ('/user/listTokens', ListTokensHandler),
    ('/user/getInviteCode', GetInviteCodeHandler),
    ('/user/getNewToken', GetNewTokenHandler),
    ('/user/add', AddUsersHandler),
    (OAUTH_DECORATOR.callback_path, OAUTH_DECORATOR.callback_handler()),
], debug=True)

# This is the only way to catch exceptions from the oauth decorators.
app.error_handlers[500] = Handle500
