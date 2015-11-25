"""Module to manage the OAuth 2.0 flow and credentials."""

from datastore import OAuth
from oauth2client.appengine import OAuth2Decorator

# TODO(eholder): Add a test for this. Not sure how yet.
scopes = []
scopes.append('https://www.googleapis.com/auth/admin.directory.user')
scopes.append('https://www.googleapis.com/auth/admin.directory.group')
scopes.append('https://www.googleapis.com/auth/admin.directory.group.member')
oauth_decorator = OAuth2Decorator(
    client_id=OAuth.GetOrInsertDefault().client_id,
    client_secret=OAuth.GetOrInsertDefault().client_secret,
    scope=scopes)
