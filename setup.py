"""The setup module for first-time initialization of the app."""

import admin
from appengine_config import JINJA_ENVIRONMENT
from config import PATHS
from datastore import User
from datastore import OAuth
from datastore import DomainVerification
from error_handlers import Handle500
import webapp2
import xsrf




def _RenderSetupOAuthClientTemplate():
  """Render a setup page with inputs for client id and secret."""
  entity = OAuth.GetOrInsertDefault()
  domain_verification = DomainVerification.GetOrInsertDefault()
  template_values = {
      'client_id': entity.client_id,
      'client_secret': entity.client_secret,
      'dv_content': domain_verification.content,
  }
  template = JINJA_ENVIRONMENT.get_template('templates/setup_client.html')
  return template.render(template_values)


class SetupOAuthClientHandler(webapp2.RequestHandler):

  """Setup a client in the datastore."""

  @admin.RequireAppAdmin
  def get(self):
    """Output the oauth and domain verification template."""
    self.response.write(_RenderSetupOAuthClientTemplate())

  @admin.RequireAppAdmin
  @xsrf.XSRFProtect
  def post(self):
    """Store client id, client secret, and domain verification content."""
    client_id = self.request.get('client_id')
    client_secret = self.request.get('client_secret')
    OAuth.Update(client_id, client_secret)
    OAuth.Flush()
    dv_content = self.request.get('dv_content')
    DomainVerification.Update(dv_content)
    if User.GetCount() > 0:
      self.redirect(PATHS['user_page_path'])
    else:
      self.redirect(PATHS['user_add_path'])


APP = webapp2.WSGIApplication([
    (PATHS['setup_oauth_path'], SetupOAuthClientHandler),
], debug=True)

# This is the only way to catch exceptions from the oauth decorators.
APP.error_handlers[500] = Handle500
