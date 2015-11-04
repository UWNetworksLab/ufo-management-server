"""Admin protection for authenticated users."""

import logging

from google.appengine.api import users


def require_admin(func):
  """Decorator to require the user to be an admin."""
  def decorate(self, *args, **kwargs):
    user = users.get_current_user()
    if not user:
      logging.error('user is not logged in')
      self.abort(403)
    if not users.is_current_user_admin():
      logging.error('user is not an admin')
      self.abort(403)
    return func(self, *args, **kwargs)

  return decorate

