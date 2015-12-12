"""Test user module functionality."""
from mock import MagicMock
from mock import patch
import sys

import base64
from datastore import User
from googleapiclient import errors
from google.appengine.ext import ndb
import google_directory_service
import hashlib
import json

import unittest
import webtest

# Need to mock the decorator at function definition time, i.e. when the module
# is loaded. http://stackoverflow.com/a/7667621/2830207
def NoOpDecorator(func):
  """Mock decorator that passes through any function for testing."""
  return func

MOCK_ADMIN = MagicMock()
MOCK_ADMIN.OAUTH_DECORATOR.oauth_required = NoOpDecorator
MOCK_ADMIN.RequireAppAndDomainAdmin = NoOpDecorator
sys.modules['admin'] = MOCK_ADMIN

MOCK_XSRF = MagicMock()
MOCK_XSRF.XSRFProtect = NoOpDecorator
sys.modules['xsrf'] = MOCK_XSRF

import user


FAKE_EMAIL = 'fake_email@example.com'
FAKE_NAME = 'fake name'
FAKE_PUBLIC_KEY = 'fakePublicKey'
FAKE_PRIVATE_KEY = 'fakePrivateKey'
FAKE_DS_KEY = 'urlEncodedKeyFromTheDatastore'
FAKE_USER_KEY = ndb.Key(User, hashlib.sha256(FAKE_EMAIL).hexdigest())
FAKE_USER = User(key=FAKE_USER_KEY, email=FAKE_EMAIL,
                 name=FAKE_NAME, public_key=FAKE_PUBLIC_KEY,
                 private_key=FAKE_PRIVATE_KEY, is_key_revoked=False)
FAKE_USER_ARRAY = []
FAKE_EMAIL_1 = u'foo@business.com'
FAKE_EMAIL_2 = u'bar@business.com'
FAKE_ADD_USER = {}
FAKE_ADD_USER['primaryEmail'] = FAKE_EMAIL_1
FAKE_ADD_USER['name'] = {}
FAKE_ADD_USER['name']['fullName'] = FAKE_NAME
FAKE_ADD_USER['email'] = FAKE_EMAIL_1
FAKE_ADD_USER['role'] = 'MEMBER'
FAKE_ADD_USER['type'] = 'USER'
FAKE_USER_ARRAY.append(FAKE_ADD_USER)


class UserTest(unittest.TestCase):

  """Test user class functionality."""

  # pylint: disable=too-many-public-methods

  def setUp(self):
    self.testapp = webtest.TestApp(user.APP)

  @patch('user._RenderLandingTemplate')
  def testLandingPageHandler(self, mock_landing_template):
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

  @patch('user.User.GetByKey')
  @patch('user._MakeInviteCode')
  @patch('user._RenderUserDetailsTemplate')
  def testGetInviteCodeHandler(self, mock_user_template, mock_make_invite_code,
                               mock_get_user):
    mock_get_user.return_value = FAKE_USER
    fake_invite_code = 'base64EncodedBlob'
    mock_make_invite_code.return_value = fake_invite_code

    self.testapp.get('/user/getInviteCode?key=%s' % FAKE_DS_KEY)

    mock_get_user.assert_called_once_with(FAKE_DS_KEY)
    mock_make_invite_code.assert_called_once_with(FAKE_USER)
    mock_user_template.assert_called_once_with(FAKE_USER, fake_invite_code)

  @patch('user._RenderUserDetailsTemplate')
  @patch('user.User.GetByKey')
  @patch('user.User.UpdateKeyPair')
  def testGetNewKeyPairHandler(self, mock_update, mock_get_by_key,
                               mock_render_details):
    mock_get_by_key.return_value = FAKE_USER

    self.testapp.get('/user/getNewKeyPair?key=%s' % FAKE_DS_KEY)

    mock_update.assert_called_once_with(FAKE_DS_KEY)
    mock_get_by_key.assert_called_once_with(FAKE_DS_KEY)
    mock_render_details.assert_called_once_with(FAKE_USER)

  @patch('user._RenderAddUsersTemplate')
  @patch('google_directory_service.GoogleDirectoryService.GetUserAsList')
  @patch('google_directory_service.GoogleDirectoryService.GetUsersByGroupKey')
  @patch('google_directory_service.GoogleDirectoryService.GetUsers')
  @patch('google_directory_service.GoogleDirectoryService.__init__')
  def testAddUsersGetHandlerNoParam(self, mock_ds, mock_get_users,
                                    mock_get_by_key, mock_get_user,
                                    mock_render):
    # pylint: disable=too-many-arguments
    self.testapp.get('/user/add')

    mock_ds.assert_not_called()
    mock_get_users.assert_not_called()
    mock_get_user.assert_not_called()
    mock_get_by_key.assert_not_called()
    mock_render.assert_called_once_with([])

  @patch('user._RenderAddUsersTemplate')
  @patch('google_directory_service.GoogleDirectoryService.GetUserAsList')
  @patch('google_directory_service.GoogleDirectoryService.GetUsersByGroupKey')
  @patch('google_directory_service.GoogleDirectoryService.GetUsers')
  @patch.object(google_directory_service.GoogleDirectoryService, '__init__')
  def testAddUsersGetHandlerWithGroup(self, mock_ds, mock_get_users,
                                      mock_get_by_key, mock_get_user,
                                      mock_render):
    # pylint: disable=too-many-arguments
    mock_ds.return_value = None
    # Email address could refer to group or user
    group_key = 'foo@bar.mybusiness.com'
    mock_get_by_key.return_value = FAKE_USER_ARRAY
    self.testapp.get('/user/add?group_key=' + group_key)

    mock_get_users.assert_not_called()
    mock_get_user.assert_not_called()
    mock_ds.assert_called_once_with(MOCK_ADMIN.OAUTH_DECORATOR)
    mock_get_by_key.assert_called_once_with(group_key)
    mock_render.assert_called_once_with(FAKE_USER_ARRAY)

  @patch('user._RenderAddUsersTemplate')
  @patch('google_directory_service.GoogleDirectoryService.GetUserAsList')
  @patch('google_directory_service.GoogleDirectoryService.GetUsersByGroupKey')
  @patch('google_directory_service.GoogleDirectoryService.GetUsers')
  @patch('google_directory_service.GoogleDirectoryService.__init__')
  def testAddUsersGetHandlerWithUser(self, mock_ds, mock_get_users,
                                     mock_get_by_key, mock_get_user,
                                     mock_render):
    # pylint: disable=too-many-arguments
    mock_ds.return_value = None
    # Email address could refer to group or user
    user_key = 'foo@bar.mybusiness.com'
    mock_get_user.return_value = FAKE_USER_ARRAY
    self.testapp.get('/user/add?user_key=' + user_key)

    mock_get_users.assert_not_called()
    mock_get_by_key.assert_not_called()
    mock_ds.assert_called_once_with(MOCK_ADMIN.OAUTH_DECORATOR)
    mock_get_user.assert_called_once_with(user_key)
    mock_render.assert_called_once_with(FAKE_USER_ARRAY)

  @patch('user._RenderAddUsersTemplate')
  @patch('google_directory_service.GoogleDirectoryService.GetUserAsList')
  @patch('google_directory_service.GoogleDirectoryService.GetUsersByGroupKey')
  @patch('google_directory_service.GoogleDirectoryService.GetUsers')
  @patch('google_directory_service.GoogleDirectoryService.__init__')
  def testAddUsersGetHandlerWithAll(self, mock_ds, mock_get_users,
                                    mock_get_by_key, mock_get_user,
                                    mock_render):
    # pylint: disable=too-many-arguments
    mock_ds.return_value = None
    mock_get_users.return_value = FAKE_USER_ARRAY
    self.testapp.get('/user/add?get_all=true')

    mock_get_by_key.assert_not_called()
    mock_get_user.assert_not_called()
    mock_ds.assert_called_once_with(MOCK_ADMIN.OAUTH_DECORATOR)
    mock_get_users.assert_called_once_with()
    mock_render.assert_called_once_with(FAKE_USER_ARRAY)

  @patch('user._RenderAddUsersTemplate')
  @patch('google_directory_service.GoogleDirectoryService.GetUserAsList')
  @patch('google_directory_service.GoogleDirectoryService.GetUsersByGroupKey')
  @patch('google_directory_service.GoogleDirectoryService.GetUsers')
  @patch('google_directory_service.GoogleDirectoryService.__init__')
  def testAddUsersGetHandlerWithError(self, mock_ds, mock_get_users,
                                      mock_get_by_key, mock_get_user,
                                      mock_render):
    # pylint: disable=too-many-arguments
    fake_status = '404'
    fake_response = MagicMock(status=fake_status)
    fake_content = b'some error content'
    fake_error = errors.HttpError(fake_response, fake_content)
    mock_ds.side_effect = fake_error
    mock_get_users.return_value = FAKE_USER_ARRAY
    self.testapp.get('/user/add?get_all=true')

    mock_ds.assert_called_once_with(MOCK_ADMIN.OAUTH_DECORATOR)
    mock_get_by_key.assert_not_called()
    mock_get_user.assert_not_called()
    mock_get_users.assert_not_called()
    mock_render.assert_called_once_with([], fake_error)

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
    data = '?selected_user={0}&selected_user={1}'.format(user_1, user_2)
    response = self.testapp.post('/user/add' + data)

    mock_insert.assert_called_once_with(user_array)
    self.assertEqual(response.status_int, 302)
    self.assertTrue('/user' in response.location)

  @patch('user._RenderUserDetailsTemplate')
  @patch('user.User.GetByKey')
  @patch('user.User.ToggleKeyRevoked')
  def testToggleKeyRevokedHandler(self, mock_toggle_key_revoked,
                                  mock_get_by_key, mock_render_details):
    mock_get_by_key.return_value = FAKE_USER

    self.testapp.get('/user/toggleRevoked?key=%s' % FAKE_DS_KEY)

    mock_toggle_key_revoked.assert_called_once_with(FAKE_DS_KEY)
    mock_get_by_key.assert_called_once_with(FAKE_DS_KEY)
    mock_render_details.assert_called_once_with(FAKE_USER)

  @patch('user._RenderUserDetailsTemplate')
  @patch('user.User.GetByKey')
  def testGetUserDetailsHandler(self, mock_get_by_key, mock_render_details):
    mock_get_by_key.return_value = FAKE_USER

    self.testapp.get('/user/details?key=%s' % FAKE_DS_KEY)

    mock_get_by_key.assert_called_once_with(FAKE_DS_KEY)
    mock_render_details.assert_called_once_with(FAKE_USER)

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
    self.assertEquals('Add Users' in user_list_template, True)
    click_user_string = 'Click a user below to view more details.'
    self.assertEquals(click_user_string in user_list_template, True)
    self.assertEquals(FAKE_USER.email in user_list_template, True)
    details_link = ('user/details?key=' + FAKE_DS_KEY)
    self.assertEquals(details_link in user_list_template, True)

  @patch('datastore.DomainVerification.GetOrInsertDefault')
  def testRenderLandingTemplate(self, mock_domain_verif):
    fake_content = 'foobarbaz'
    fake_domain_verif = MagicMock(content=fake_content)
    mock_domain_verif.return_value = fake_domain_verif

    landing_template = user._RenderLandingTemplate()

    mock_domain_verif.assert_called_once_with()
    self.assertTrue(fake_content in landing_template)

  def testRenderAddUsersWithNoUsers(self):
    add_users_template = user._RenderAddUsersTemplate([])
    no_user_string = 'No users found. Try another query below.'
    self.assertTrue(no_user_string in add_users_template)
    self.assertTrue('xsrf' not in add_users_template)
    self.assertTrue('An error occurred while' not in add_users_template)

  def testRenderAddUsersWithUsers(self):
    add_users_template = user._RenderAddUsersTemplate(FAKE_USER_ARRAY)
    self.assertTrue('Add Selected Users' in add_users_template)
    self.assertTrue('xsrf' in add_users_template)
    self.assertTrue('An error occurred while' not in add_users_template)

  def testRenderAddUsersWithError(self):
    fake_error = 'foo bar happened causing baz'
    add_users_template = user._RenderAddUsersTemplate([], fake_error)
    self.assertTrue('An error occurred while' in add_users_template)
    self.assertTrue(fake_error in add_users_template)

  @patch.object(user.User, 'key')
  def testRenderUserDetailTemplate(self, mock_url_key):
    mock_url_key.urlsafe.return_value = FAKE_DS_KEY

    user_details_template = user._RenderUserDetailsTemplate(FAKE_USER)

    self.assertEqual(FAKE_NAME in user_details_template, True)
    self.assertEqual(FAKE_EMAIL in user_details_template, True)
    self.assertEqual(FAKE_PUBLIC_KEY in user_details_template, True)
    self.assertEqual(FAKE_PRIVATE_KEY in user_details_template, True)
    self.assertEqual(FAKE_DS_KEY in user_details_template, True)
    self.assertEqual('Enabled' in user_details_template, True)
    self.assertEquals('Invite Code Below' in user_details_template, False)

  @patch.object(user.User, 'key')
  def testRenderUserDetailInviteCode(self, mock_url_key):
    fake_invite_code = 'foo bar baz in base64 blob'
    mock_url_key.urlsafe.return_value = FAKE_DS_KEY

    user_details_template = user._RenderUserDetailsTemplate(FAKE_USER,
                                                            fake_invite_code)

    self.assertEqual(FAKE_NAME in user_details_template, True)
    self.assertEqual(FAKE_EMAIL in user_details_template, True)
    self.assertEqual(FAKE_PUBLIC_KEY in user_details_template, True)
    self.assertEqual(FAKE_PRIVATE_KEY in user_details_template, True)
    self.assertEqual(FAKE_DS_KEY in user_details_template, True)
    self.assertEqual('Enabled' in user_details_template, True)
    self.assertEquals('Invite Code Below' in user_details_template, True)
    self.assertEquals(fake_invite_code in user_details_template, True)

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
    invite_code_data = json.loads(json_string)

    mock_get_ip.assert_called_once_with()
    self.assertEqual('Cloud',
                     invite_code_data['networkName'])
    self.assertEqual(FAKE_USER.email,
                     invite_code_data['networkData']['user'])
    self.assertEqual(FAKE_USER.private_key,
                     invite_code_data['networkData']['pass'])
    self.assertEqual(fake_ip,
                     invite_code_data['networkData']['host'])

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
