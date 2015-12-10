"""Admin protection for authenticated users."""


from datastore import OAuth
from googleapiclient import errors
from google.appengine.api import users
from google_directory_service import GoogleDirectoryService
import logging
from oauth2client.appengine import OAuth2Decorator

# TODO(eholder): Add tests for this. Probably should test that we only
# request the scopes we need and that the decorator is called with the
# id and secret as intended.
USER = 'https://www.googleapis.com/auth/admin.directory.user'
GROUP = 'https://www.googleapis.com/auth/admin.directory.group.readonly'
MEMBER = 'https://www.googleapis.com/auth/admin.directory.group.member.readonly'
SCOPES = [USER, GROUP, MEMBER]


def RequireAppAdmin(func):
  """Decorator to require the user to be an admin."""
  def decorate(self, *args, **kwargs):
    """Actual decorate function that requires admin.

    Args:
      args: Parameters passed on to the specified function if successful.
      kwargs: Parameters passed on to the specified function if successful.
    """
    user = users.get_current_user()
    if not user:
      logging.error('user is not logged in')
      self.abort(403)
    if not users.is_current_user_admin():
      logging.error('user is not an admin')
      self.abort(403)
    return func(self, *args, **kwargs)

  return decorate


def RequireAppAndDomainAdmin(oauth_decorator):
  """Decorator to require the user to be an admin."""
  def Wrap(func):
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

      directory_user = None
      try:
        directory_service = GoogleDirectoryService(oauth_decorator)
        directory_user = directory_service.GetUser(identifier)
      except errors.HttpError:
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
  return Wrap


OAUTH_ALL_SCOPES_DECORATOR = OAuth2Decorator(
    client_id=OAuth.GetOrInsertDefault().client_id,
    client_secret=OAuth.GetOrInsertDefault().client_secret,
    scope=SCOPES)

OAUTH_USER_SCOPE_DECORATOR = OAuth2Decorator(
    client_id=OAuth.GetOrInsertDefault().client_id,
    client_secret=OAuth.GetOrInsertDefault().client_secret,
    scope=USER)

