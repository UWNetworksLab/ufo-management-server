"""Module to manage the OAuth 2.0 flow and credentials."""

from datastore import OAuth
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
