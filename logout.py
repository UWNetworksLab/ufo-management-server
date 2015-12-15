"""The logout module to facilitate testing switching between admin users."""

from config import PATHS
from google.appengine.api import users
import webapp2


class LogoutHandler(webapp2.RequestHandler):

  """Logs the current user out."""

	# pylint: disable=too-few-public-methods

  def get(self):
    """Log the user out and point the login address to the default path."""
    logout_url = users.create_logout_url(PATHS['user_page_path'])
    self.redirect(logout_url)


APP = webapp2.WSGIApplication([
    (PATHS['logout'], LogoutHandler),
], debug=True)
