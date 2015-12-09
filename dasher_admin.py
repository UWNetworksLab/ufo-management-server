"""Dasher admin protection for authenticated users."""

from auth import OAUTH_DECORATOR
from googleapiclient import errors
from google.appengine.api import users
from google_directory_service import GoogleDirectoryService
import logging


def DasherAdminAuthRequired(func):
  """Decorator to require the user to be an admin."""
  def decorate(self, *args, **kwargs):
    """Actual decorate function that requires admin.

    Args:
      args: Parameters passed on to the specified function if successful.
      kwargs: Parameters passed on to the specified function if successful.
    """
    user = users.get_current_user()
    if not user or user is None:
      logging.error('User is not logged in.')
      self.abort(403)

    identifier = user.email()
    if identifier is None or identifier is '':
      logging.error('No identifier found for the user.')
      self.abort(403)

    directory_service = GoogleDirectoryService(OAUTH_DECORATOR)
    directory_user = None
    try:
      directory_user = directory_service.GetUser(identifier)
    except errors.HttpError as error:
      logging.error('Exception when asking dasher for this user.')
      self.abort(403)

    if not directory_user or directory_user is None:
      logging.error('User was not found in dasher.')
      self.abort(403)
    if not directory_user['isAdmin']:
      logging.error('User is not a dasher admin.')
      self.abort(403)
    return func(self, *args, **kwargs)

  return decorate

