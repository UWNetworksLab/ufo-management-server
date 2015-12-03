"""The setup module for first-time initialization of the app."""

from appengine_config import JINJA_ENVIRONMENT
from auth import oauth_decorator
from datastore import User
from datastore import OAuth
from datastore import DomainVerification
from error_handlers import Handle500
from google.appengine.api import app_identity
import json
import webapp2
import xsrf
import admin


JINJA_ENVIRONMENT.globals['xsrf_token'] = xsrf.xsrf_token()


def _RenderSetupOAuthClientTemplate():
  """Render a setup page with inputs for client id and secret."""
  entity = OAuth.GetOrInsertDefault()
  domain_verification = DomainVerification.GetOrInsertDefault()
  template_values = {
      'host': app_identity.get_default_version_hostname(),
      'client_id': entity.client_id,
      'client_secret': entity.client_secret,
      'dv_content': domain_verification.content,
  }
  template = JINJA_ENVIRONMENT.get_template('templates/setup_client.html')
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
    OAuth.Update(client_id, client_secret)
    OAuth.Flush()
    dv_content = self.request.get('dv_content')
    DomainVerification.Update(dv_content)
    if User.GetCount() > 0:
      self.redirect('/user')
    else:
      self.redirect('/user/add')


app = webapp2.WSGIApplication([
    ('/setup/oauthclient', SetupOAuthClientHandler),
    (oauth_decorator.callback_path, oauth_decorator.callback_handler()),
], debug=True)

# This is the only way to catch exceptions from the oauth decorators.
app.error_handlers[500] = Handle500
