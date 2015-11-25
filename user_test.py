from mock import MagicMock
from mock import patch
import sys

from datastore import User
from google.appengine.ext import ndb
import hashlib

import unittest
import webapp2
import webtest

# Need to mock the decorator at function definition time, i.e. when the module
# is loaded. http://stackoverflow.com/a/7667621/2830207
def noop_decorator(func):
  return func

mock_auth = MagicMock()
mock_auth.oauth_decorator.oauth_required = noop_decorator
sys.modules['auth'] = mock_auth
import user


FAKE_EMAIL = 'fake_email@example.com'
FAKE_NAME = 'fake name'
FAKE_PUBLIC_KEY = 'fakePublicKey'
FAKE_PRIVATE_KEY = 'fakePrivateKey'
FAKE_DS_KEY = 'urlEncodedKeyFromTheDatastore'
FAKE_USER_KEY = ndb.Key(User, hashlib.sha256(FAKE_EMAIL).hexdigest())
FAKE_USER = User(key=FAKE_USER_KEY, email=FAKE_EMAIL,
                 name=FAKE_NAME, public_key=FAKE_PUBLIC_KEY,
                 private_key=FAKE_PRIVATE_KEY)


class UserTest(unittest.TestCase):

  def setUp(self):
    self.testapp = webtest.TestApp(user.app)

  @patch('user._RenderLandingTemplate')
  def testListUsersHandler(self, mock_landing_template):
    self.testapp.get('/')
    mock_landing_template.assert_called_once_with()

  @patch('user._RenderUserListTemplate')
  def testListUsersHandler(self, mock_user_template):
    self.testapp.get('/user')
    mock_user_template.assert_called_once_with()

  @patch('user.User.DeleteByKey')
  @patch('user._RenderUserListTemplate')
  def testDeleteUserHandler(self, mock_user_template,
                            mock_delete_user):
    self.testapp.get('/user/delete?key=%s' % FAKE_DS_KEY)
    mock_delete_user.assert_called_once_with(FAKE_DS_KEY)
    mock_user_template.assert_called_once_with()

  @patch('user._RenderTokenListTemplate')
  def testListTokensHandler(self, mock_token_template):
    self.testapp.get('/user/listTokens')
    mock_token_template.assert_called_once_with()

  @patch('user.User._UpdateKeyPair')
  @patch('user._RenderTokenListTemplate')
  def testGetNewTokenHandler(self, mock_token_template,
                             mock_update):
    self.testapp.get('/user/getNewToken?key=%s' % FAKE_DS_KEY)
    mock_update.assert_called_once_with(FAKE_DS_KEY)
    mock_token_template.assert_called_once_with()

  @patch('user._GenerateUserPayload')
  @patch('user.User.GetAll')
  def testRenderUserListTemplate(self, mock_get_all, mock_generate):
    fake_users = [FAKE_USER]
    mock_get_all.return_value = fake_users
    fake_dictionary = {}
    fake_dictionary[FAKE_DS_KEY] = FAKE_USER.email
    mock_generate.return_value = fake_dictionary

    user_list_template = user._RenderUserListTemplate()

    mock_get_all.assert_called_once_with()
    mock_generate.assert_called_once_with(fake_users)
    self.assertTrue('List Tokens' in user_list_template)
    self.assertTrue(FAKE_USER.email in user_list_template)
    self.assertTrue(
        ('user/delete?key=' + FAKE_DS_KEY) in user_list_template)
    self.assertTrue(
        ('user/getNewToken?key=' + FAKE_DS_KEY) in user_list_template)

  @patch('user._GenerateTokenPayload')
  @patch('user.User.GetAll')
  def testRenderTokenListTemplate(self, mock_get_all, mock_generate):
    fake_users = [FAKE_USER]
    mock_get_all.return_value = fake_users
    fake_dictionary = {}
    fake_tuple = (FAKE_USER.email, FAKE_USER.public_key)
    fake_dictionary[FAKE_DS_KEY] = fake_tuple
    mock_generate.return_value = fake_dictionary

    token_list_template = user._RenderTokenListTemplate()

    mock_get_all.assert_called_once_with()
    mock_generate.assert_called_once_with(fake_users)
    self.assertTrue('token_payload:' in token_list_template)
    self.assertTrue(FAKE_USER.email in token_list_template)
    self.assertTrue(
        ('user/getNewToken?key=' + FAKE_DS_KEY) in token_list_template)

  @patch('datastore.DomainVerification.GetOrInsertDefault')
  def testRenderLandingTemplate(self, mock_domain_verif):
    fake_content = 'foobarbaz'
    fake_domain_verif = MagicMock(content=fake_content)
    mock_domain_verif.return_value = fake_domain_verif

    landing_template = user._RenderLandingTemplate()

    mock_domain_verif.assert_called_once_with()
    self.assertTrue(fake_content in landing_template)

  @patch.object(user.User, 'key')
  def testGenerateTokenPayload(self, mock_url_key):
    mock_url_key.urlsafe.return_value = FAKE_DS_KEY
    fake_users = [FAKE_USER]

    user_token_payloads = user._GenerateTokenPayload(fake_users)

    tup1 = (FAKE_USER.email, FAKE_USER.public_key)
    self.assertEqual(user_token_payloads[FAKE_DS_KEY], tup1)

    self.assertTrue(FAKE_USER.private_key not in user_token_payloads)
    self.assertTrue(FAKE_USER.private_key not in user_token_payloads[FAKE_DS_KEY])

  @patch.object(user.User, 'key')
  def testGenerateUserPayload(self, mock_url_key):
    mock_url_key.urlsafe.return_value = FAKE_DS_KEY
    fake_users = [FAKE_USER]

    user_payloads = user._GenerateUserPayload(fake_users)

    self.assertEqual(user_payloads[FAKE_DS_KEY], FAKE_USER.email)

    self.assertTrue(FAKE_USER.public_key not in user_payloads)
    self.assertTrue(FAKE_USER.public_key not in user_payloads[FAKE_DS_KEY])
    self.assertTrue(FAKE_USER.private_key not in user_payloads)
    self.assertTrue(FAKE_USER.private_key not in user_payloads[FAKE_DS_KEY])

if __name__ == '__main__':
    unittest.main()
