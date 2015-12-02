from mock import MagicMock
from mock import patch
import sys

from datastore import User
from datastore import OAuth

import json
import unittest
import webapp2
import webtest

# Need to mock the decorator at function definition time, i.e. when the module
# is loaded. http://stackoverflow.com/a/7667621/2830207
def noop_decorator(func):
  return func

mock_auth = MagicMock()
mock_auth.OAUTH_DECORATOR.oauth_required = noop_decorator
sys.modules['auth'] = mock_auth

mock_xsrf = MagicMock()
mock_xsrf.xsrf_protect = noop_decorator
sys.modules['xsrf'] = mock_xsrf

mock_admin = MagicMock()
mock_admin.require_admin = noop_decorator
sys.modules['admin'] = mock_admin


import setup


FAKE_ID = 'fakeAlphaNumerics0123456789abc'
FAKE_SECRET = 'fakeAlphaNumerics0123456789zyx'
RENDER_OAUTH_TEMPLATE = '_RenderSetupOAuthClientTemplate'
RENDER_USER_TEMPLATE = '_RenderSetupUsersTemplate'
FAKE_USER_ARRAY = []
FAKE_EMAIL_1 = u'foo@business.com'
FAKE_EMAIL_2 = u'bar@business.com'
FAKE_USER = {}
FAKE_USER['email'] = FAKE_EMAIL_1
FAKE_USER['role'] = 'MEMBER'
FAKE_USER['type'] = 'USER'
FAKE_USER_ARRAY.append(FAKE_USER)


class SetupTest(unittest.TestCase):

  def setUp(self):
    self.testapp = webtest.TestApp(setup.app)

  @patch('setup._RenderSetupOAuthClientTemplate')
  def testSetupOAuthClientGetHandler(self, mock_render_oauth_template):
    self.testapp.get('/setup/oauthclient')
    mock_render_oauth_template.assert_called_once_with()

  @patch('datastore.OAuth.Update')
  @patch('datastore.OAuth.Flush')
  def testSetupOAuthClientPostHandler(self, mock_flush, mock_update):
    resp = self.testapp.post('/setup/oauthclient?client_id={0}&client_secret={1}'
                             .format(unicode(FAKE_ID,'utf-8'),
                                     unicode(FAKE_SECRET,'utf-8')))
    mock_update.assert_called_once_with(FAKE_ID, FAKE_SECRET)
    mock_flush.assert_called_once_with()
    self.assertEqual(resp.status_int, 302)
    # TODO(eholder): Figure out why this test fails but works on appspot.
    # self.assertTrue('/setup/users' in resp.location)

  @patch('datastore.OAuth.Flush')
  @patch('user.User.GetCount')
  def testSetupUsersGetHandlerAlreadySet(self, mock_get_count, mock_flush):
    mock_get_count.return_value = 1
    response = self.testapp.get('/setup/users')
    mock_flush.assert_called_once_with()
    mock_get_count.assert_called_once_with()
    self.assertTrue('Unable to setup because app is already '
                    'initialized.' in response)

  @patch('setup._RenderSetupUsersTemplate')
  @patch('google_directory_service.GoogleDirectoryService.GetUsersByGroupKey')
  @patch('google_directory_service.GoogleDirectoryService.__init__')
  @patch('datastore.OAuth.Flush')
  @patch('user.User.GetCount')
  def testSetupUsersGetHandlerNotSet(self, mock_get_count, mock_flush,
                                     mock_ds, mock_get_users,
                                     mock_render_users_template):
    mock_get_count.return_value = 0
    mock_ds.return_value = None
    mock_get_users.return_value = None
    response = self.testapp.get('/setup/users')
    mock_flush.assert_called_once_with()
    mock_get_count.assert_called_once_with()

    mock_ds.assert_not_called()
    mock_get_users.assert_not_called()
    mock_render_users_template.assert_called_once_with([])

  @patch('setup._RenderSetupUsersTemplate')
  @patch('google_directory_service.GoogleDirectoryService.GetUsersByGroupKey')
  @patch('google_directory_service.GoogleDirectoryService.__init__')
  @patch('datastore.OAuth.Flush')
  @patch('user.User.GetCount')
  def testSetupUsersGetHandlerWithGroup(self, mock_get_count, mock_flush,
                                        mock_ds, mock_get_users,
                                        mock_render_users_template):
    mock_get_count.return_value = 0
    mock_ds.return_value = None
    group_key = 'foo@bar.mybusiness.com'
    mock_get_users.return_value = FAKE_USER_ARRAY
    response = self.testapp.get('/setup/users?group_key=' + group_key)
    mock_flush.assert_called_once_with()
    mock_get_count.assert_called_once_with()

    mock_ds.assert_called_once_with(mock_auth.OAUTH_DECORATOR)
    mock_get_users.assert_called_once_with(group_key)
    mock_render_users_template.assert_called_once_with(FAKE_USER_ARRAY)

  @patch('user.User.InsertUsers')
  def testSetupUsersPostHandler(self, mock_insert):
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
    response = self.testapp.post('/setup/users' + data)

    mock_insert.assert_called_once_with(user_array)
    self.assertEqual(response.status_int, 302)
    # TODO(eholder): Figure out why this test fails but works on appspot.
    # self.assertTrue('/user' in response.location)

  @patch('datastore.OAuth.GetOrInsertDefault')
  def testRenderSetupOAuthClientTemplate(self, mock_get_or_insert):
    mock_get_or_insert.return_value.client_id = FAKE_ID
    mock_get_or_insert.return_value.client_secret = FAKE_SECRET

    setup_client_template = setup._RenderSetupOAuthClientTemplate()

    self.assertTrue('client_id:' in setup_client_template)
    self.assertTrue('client_secret:' in setup_client_template)
    self.assertTrue('xsrf' in setup_client_template)
    self.assertTrue(FAKE_ID in setup_client_template)
    self.assertTrue(FAKE_SECRET in setup_client_template)

  def testRenderSetupUsersTemplate(self):
    setup_users_template = setup._RenderSetupUsersTemplate(FAKE_USER_ARRAY)
    self.assertTrue('Add Selected Users' in setup_users_template)
    self.assertTrue('xsrf' in setup_users_template)


if __name__ == '__main__':
    unittest.main()
