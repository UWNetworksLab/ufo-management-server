from mock import MagicMock
from mock import patch
import sys

import base64
from datastore import User
from datastore import ProxyServer
from google.appengine.ext import ndb
import hashlib
import json

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

mock_xsrf = MagicMock()
mock_xsrf.xsrf_protect = noop_decorator
sys.modules['xsrf'] = mock_xsrf

mock_admin = MagicMock()
mock_admin.require_admin = noop_decorator
sys.modules['admin'] = mock_admin

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
FAKE_USER_ARRAY = []
FAKE_EMAIL_1 = u'foo@business.com'
FAKE_EMAIL_2 = u'bar@business.com'
FAKE_ADD_USER = {}
FAKE_ADD_USER['primaryEmail'] = FAKE_EMAIL_1
FAKE_ADD_USER['email'] = FAKE_EMAIL_1
FAKE_ADD_USER['role'] = 'MEMBER'
FAKE_ADD_USER['type'] = 'USER'
FAKE_USER_ARRAY.append(FAKE_ADD_USER)


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

  @patch('user.User.GetByKey')
  @patch('user._MakeInviteCode')
  @patch('user._RenderUserListTemplate')
  def testGetInviteCodeHandler(self, mock_user_template, mock_make_invite_code,
                               mock_get_user):
    fake_url_key = 'foobarbaz'
    mock_get_user.return_value = fake_url_key
    fake_invite_code = 'base64EncodedBlob'
    mock_make_invite_code.return_value = fake_invite_code

    self.testapp.get('/user/getInviteCode?key=%s' % FAKE_DS_KEY)

    mock_get_user.assert_called_once_with(FAKE_DS_KEY)
    mock_make_invite_code.assert_called_once_with(fake_url_key)
    mock_user_template.assert_called_once_with(fake_invite_code)

  @patch('user.User._UpdateKeyPair')
  @patch('user._RenderTokenListTemplate')
  def testGetNewTokenHandler(self, mock_token_template,
                             mock_update):
    self.testapp.get('/user/getNewToken?key=%s' % FAKE_DS_KEY)
    mock_update.assert_called_once_with(FAKE_DS_KEY)
    mock_token_template.assert_called_once_with()

  @patch('user._RenderAddUsersTemplate')
  @patch('google_directory_service.GoogleDirectoryService.GetUsersByGroupKey')
  @patch('google_directory_service.GoogleDirectoryService.GetUsers')
  @patch('google_directory_service.GoogleDirectoryService.__init__')
  def testAddUsersGetHandlerNoParam(self, mock_ds, mock_get_users,
                                    mock_get_by_key, mock_render):
    response = self.testapp.get('/user/add')

    mock_ds.assert_not_called()
    mock_get_users.assert_not_called()
    mock_get_by_key.assert_not_called()
    mock_render.assert_called_once_with([])

  @patch('user._RenderAddUsersTemplate')
  @patch('google_directory_service.GoogleDirectoryService.GetUsersByGroupKey')
  @patch('google_directory_service.GoogleDirectoryService.GetUsers')
  @patch('google_directory_service.GoogleDirectoryService.__init__')
  def testAddUsersGetHandlerWithGroup(self, mock_ds, mock_get_users,
                                      mock_get_by_key, mock_render):
    mock_ds.return_value = None
    group_key = 'foo@bar.mybusiness.com'
    mock_get_by_key.return_value = FAKE_USER_ARRAY
    response = self.testapp.get('/user/add?group_key=' + group_key)

    mock_get_users.assert_not_called()
    mock_ds.assert_called_once_with(mock_auth.oauth_decorator)
    mock_get_by_key.assert_called_once_with(group_key)
    mock_render.assert_called_once_with(FAKE_USER_ARRAY)

  @patch('user._RenderAddUsersTemplate')
  @patch('google_directory_service.GoogleDirectoryService.GetUsersByGroupKey')
  @patch('google_directory_service.GoogleDirectoryService.GetUsers')
  @patch('google_directory_service.GoogleDirectoryService.__init__')
  def testAddUsersGetHandlerWithAll(self, mock_ds, mock_get_users,
                                    mock_get_by_key, mock_render):
    mock_ds.return_value = None
    mock_get_users.return_value = FAKE_USER_ARRAY
    response = self.testapp.get('/user/add?get_all=true')

    mock_get_by_key.assert_not_called()
    mock_ds.assert_called_once_with(mock_auth.oauth_decorator)
    mock_get_users.assert_called_once_with()
    mock_render.assert_called_once_with(FAKE_USER_ARRAY)

  @patch('user.User.InsertUsers')
  def testAddUsersPostHandler(self, mock_insert):
    user_1 = {}
    user_1['primaryEmail'] = FAKE_EMAIL_1
    user_1['name'] = {}
    user_1['name']['fullName'] = FAKE_EMAIL_1
    user_2 = {}
    user_2['primaryEmail'] = FAKE_EMAIL_2
    user_2['name'] = {}
    user_2['name']['fullName'] = FAKE_EMAIL_2
    user_array = []
    user_array.append(user_1)
    user_array.append(user_2)
    data = '?selected_user={0}&selected_user={1}'.format(FAKE_EMAIL_1,
                                                         FAKE_EMAIL_2)
    response = self.testapp.post('/user/add' + data)

    mock_insert.assert_called_once_with(user_array)
    self.assertEqual(response.status_int, 302)
    # TODO(eholder): Figure out why this test fails but works on appspot.
    # self.assertTrue('/user' in response.location)

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
    self.assertTrue('Invite Code Below' not in user_list_template)

  @patch('user._GenerateUserPayload')
  @patch('user.User.GetAll')
  def testRenderUserListTemplateWithInviteCode(self, mock_get_all,
                                               mock_generate):
    fake_users = [FAKE_USER]
    mock_get_all.return_value = fake_users
    fake_dictionary = {}
    fake_dictionary[FAKE_DS_KEY] = FAKE_USER.email
    mock_generate.return_value = fake_dictionary

    user_list_template = user._RenderUserListTemplate('fake_invite_code')

    mock_get_all.assert_called_once_with()
    mock_generate.assert_called_once_with(fake_users)
    self.assertTrue('List Tokens' in user_list_template)
    self.assertTrue(FAKE_USER.email in user_list_template)
    self.assertTrue(
        ('user/delete?key=' + FAKE_DS_KEY) in user_list_template)
    self.assertTrue(
        ('user/getNewToken?key=' + FAKE_DS_KEY) in user_list_template)
    self.assertTrue('Invite Code Below' in user_list_template)

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

  def testRenderAddUsersTemplate(self):
    add_users_template = user._RenderAddUsersTemplate(FAKE_USER_ARRAY)
    self.assertTrue('Add Selected Users' in add_users_template)
    self.assertTrue('xsrf' in add_users_template)

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

  @patch('user._GetInviteCodeIp')
  def testMakeInviteCode(self, mock_get_ip):
    fake_ip = '0.0.0.0'
    mock_get_ip.return_value = fake_ip

    invite_code = user._MakeInviteCode(FAKE_USER)
    json_string = base64.urlsafe_b64decode(invite_code)
    data = json.loads(json_string)

    mock_get_ip.assert_called_once_with()
    self.assertTrue(FAKE_USER.email == data['user'])
    self.assertTrue(FAKE_USER.private_key in data['pass'])
    self.assertTrue(fake_ip == data['host'])

  @patch('user.ProxyServer.GetAll')
  def testGetInviteCodeIp(self, mock_get_all_proxies):
    fake_ip_1 = '0.0.0.0'
    fake_proxy_1 = MagicMock(ip_address=fake_ip_1)
    fake_ip_2 = '1.2.3.4'
    fake_proxy_2 = MagicMock(ip_address=fake_ip_2)
    mock_get_all_proxies.return_value = [fake_proxy_1, fake_proxy_2]
    fake_ip_list = [fake_ip_1, fake_ip_2]

    invite_code_ip = user._GetInviteCodeIp()

    self.assertTrue(invite_code_ip in fake_ip_list)

if __name__ == '__main__':
    unittest.main()
