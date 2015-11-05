"""The logout module to facilitate testing switching between admin users."""

from google.appengine.api import users
from error_handlers import Handle500
import webapp2



class LogoutHandler(webapp2.RequestHandler):
  """Logs the current user out."""

  def get(self):
    logout_url = users.create_logout_url(self.request.url)
    self.redirect(logout_url)


app = webapp2.WSGIApplication([
    ('/logout', LogoutHandler),
], debug=True)

# This is the only way to catch exceptions from the oauth decorators.
app.error_handlers[500] = Handle500
