"""Module to manage the OAuth 2.0 flow and credentials."""

from datastore import OAuth
from oauth2client.appengine import OAuth2Decorator

oauth_decorator = OAuth2Decorator(
    client_id=OAuth.GetClientId(),
    client_secret=OAuth.GetSecret(),
    scope='https://www.googleapis.com/auth/admin.directory.user')
