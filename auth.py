"""Module to manage the OAuth 2.0 flow and credentials."""

from datastore import OAuth
from oauth2client.appengine import OAuth2Decorator

# TODO(eholder): Add tests for this. Probably should test that we only
# request the scopes we need and that the decorator is called with the
# id and secret as intended.
user = 'https://www.googleapis.com/auth/admin.directory.user'
group = 'https://www.googleapis.com/auth/admin.directory.group.readonly'
member = 'https://www.googleapis.com/auth/admin.directory.group.member.readonly'
scopes = [user, group, member]

oauth_decorator = OAuth2Decorator(
    client_id=OAuth.GetOrInsertDefault().client_id,
    client_secret=OAuth.GetOrInsertDefault().client_secret,
    scope=scopes)
