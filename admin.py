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

OAUTH_DECORATOR = OAuth2Decorator(
    client_id=OAuth.GetOrInsertDefault().client_id,
    client_secret=OAuth.GetOrInsertDefault().client_secret,
    scope=SCOPES)

def AbortIfUserIsNotLoggedIn(self, user):
  """Check if the user is logged in and abort if not.

  Args:
    user: The user to check for being logged in.
  """
  if not user or user is None:
    logging.error('User is not logged in.')
    self.abort(403)

def AbortIfUserIsNotApplicationAdmin(self):
  """Check if the user is an application admin and abort if not."""
  if not users.is_current_user_admin():
    logging.error('User is not an application admin.')
    self.abort(403)


def RequireAppAdmin(func):
  """Decorator to require the user to be an admin."""
  def decorate(self, *args, **kwargs):
    """Actual decorate function that requires admin.

    Args:
      args: Parameters passed on to the specified function if successful.
      kwargs: Parameters passed on to the specified function if successful.
    """
    user = users.get_current_user()
    AbortIfUserIsNotLoggedIn(self, user)
    AbortIfUserIsNotApplicationAdmin(self)
    return func(self, *args, **kwargs)

  return decorate


def RequireAppAndDomainAdmin(func):
  """Decorator to require the user to be an admin."""
  def decorate(self, *args, **kwargs):
    """Actual decorate function that requires admin.

    Args:
      args: Parameters passed on to the specified function if successful.
      kwargs: Parameters passed on to the specified function if successful.
    """
    user = users.get_current_user()
    AbortIfUserIsNotLoggedIn(self, user)
    AbortIfUserIsNotApplicationAdmin(self)

    identifier = user.email()
    if identifier is None or identifier is '':
      logging.error('No identifier found for the user.')
      self.abort(403)

    is_admin_user = False
    try:
      directory_service = GoogleDirectoryService(OAUTH_DECORATOR)
      is_admin_user = directory_service.IsAdminUser(identifier)
    except errors.HttpError:
      logging.error('Exception when asking dasher for this user.')
      self.abort(403)

    if not is_admin_user:
      logging.error('User is not a dasher admin.')
      self.abort(403)
    return func(self, *args, **kwargs)

  return decorate
