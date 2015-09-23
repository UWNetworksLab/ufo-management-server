"""The main module or the entry point for the management server."""

from appengine_config import JINJA_ENVIRONMENT
from auth import oauth_decorator
from datastore import User
from error_handlers import Handle500
import webapp2


class Main(webapp2.RequestHandler):

  @oauth_decorator.oauth_required
  def get(self):
    users = User.GetUsers()
    template_values = {
        'users': users
    }
    template = JINJA_ENVIRONMENT.get_template('templates/main.html')
    self.response.write(template.render(template_values))


app = webapp2.WSGIApplication([
    ('/', Main),
    (oauth_decorator.callback_path, oauth_decorator.callback_handler()),
], debug=True)

# This is the only way to catch exceptions from the oauth decorators.
app.error_handlers[500] = Handle500
