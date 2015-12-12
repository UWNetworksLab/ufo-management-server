"""Test setup module functionality."""
from mock import MagicMock
from mock import patch
import sys

import unittest
import webtest

# Need to mock the decorator at function definition time, i.e. when the module
# is loaded. http://stackoverflow.com/a/7667621/2830207
def NoOpDecorator(func):
  """Mock decorator that passes through any function for testing."""
  return func

MOCK_ADMIN = MagicMock()
MOCK_ADMIN.RequireAppAdmin = NoOpDecorator
sys.modules['admin'] = MOCK_ADMIN

MOCK_XSRF = MagicMock()
MOCK_XSRF.XSRFProtect = NoOpDecorator
sys.modules['xsrf'] = MOCK_XSRF


import setup


FAKE_ID = 'fakeAlphaNumerics0123456789abc'
# The comment below disables landscape.io checking on that line so that it
# does not think we have an actual secret stored which we do not. The
# object it is used to get has a parameter which is the actual secret. This
# however is not.
FAKE_SECRET = 'fakeAlphaNumerics0123456789zyx'  # noqa
RENDER_OAUTH_TEMPLATE = '_RenderSetupOAuthClientTemplate'
FAKE_CONTENT = 'foobar'


class SetupTest(unittest.TestCase):

  """Test setup class functionality."""

  def setUp(self):
    self.testapp = webtest.TestApp(setup.APP)

  @patch('setup._RenderSetupOAuthClientTemplate')
  def testSetupGetHandler(self, mock_render_oauth_template):
    self.testapp.get('/setup')
    mock_render_oauth_template.assert_called_once_with()

  @patch('user.User.GetCount')
  @patch('datastore.DomainVerification.Update')
  @patch('datastore.OAuth.Update')
  @patch('datastore.OAuth.Flush')
  def testSetupPostAlreadySetHandler(self, mock_flush, mock_oauth_update,
                                     mock_dv_update, mock_get_count):
    mock_get_count.return_value = 1
    post_url = ('/setup?client_id={0}&client_secret={1}' +
                '&dv_content={2}')
    resp = self.testapp.post(post_url.format(unicode(FAKE_ID, 'utf-8'),
                                             unicode(FAKE_SECRET, 'utf-8'),
                                             unicode(FAKE_CONTENT, 'utf-8')))
    mock_oauth_update.assert_called_once_with(FAKE_ID, FAKE_SECRET)
    mock_flush.assert_called_once_with()
    mock_dv_update.assert_called_once_with(FAKE_CONTENT)
    mock_get_count.assert_called_once_with()
    self.assertEqual(resp.status_int, 302)
    self.assertTrue('/user' in resp.location)

  @patch('user.User.GetCount')
  @patch('datastore.DomainVerification.Update')
  @patch('datastore.OAuth.Update')
  @patch('datastore.OAuth.Flush')
  def testSetupPostNotSetHandler(self, mock_flush, mock_oauth_update,
                                 mock_dv_update, mock_get_count):
    mock_get_count.return_value = 0
    post_url = ('/setup?client_id={0}&client_secret={1}' +
                '&dv_content={2}')
    resp = self.testapp.post(post_url.format(unicode(FAKE_ID, 'utf-8'),
                                             unicode(FAKE_SECRET, 'utf-8'),
                                             unicode(FAKE_CONTENT, 'utf-8')))
    mock_oauth_update.assert_called_once_with(FAKE_ID, FAKE_SECRET)
    mock_flush.assert_called_once_with()
    mock_dv_update.assert_called_once_with(FAKE_CONTENT)
    mock_get_count.assert_called_once_with()

    self.assertEqual(resp.status_int, 302)
    self.assertTrue('/user/add' in resp.location)

  @patch('datastore.DomainVerification.GetOrInsertDefault')
  @patch('datastore.OAuth.GetOrInsertDefault')
  def testRenderSetupTemplate(self, mock_oauth_goi, mock_dv_goi):
    mock_oauth_goi.return_value.client_id = FAKE_ID
    mock_oauth_goi.return_value.client_secret = FAKE_SECRET
    mock_dv_goi.return_value.content = FAKE_CONTENT

    setup_client_template = setup._RenderSetupOAuthClientTemplate()

    self.assertTrue('Client ID' in setup_client_template)
    self.assertTrue('Client Secret' in setup_client_template)
    self.assertTrue('Domain Verification Meta Tag Content' in setup_client_template)
    self.assertTrue('xsrf' in setup_client_template)
    self.assertTrue(FAKE_ID in setup_client_template)
    self.assertTrue(FAKE_SECRET in setup_client_template)
    self.assertTrue(FAKE_CONTENT in setup_client_template)


if __name__ == '__main__':
  unittest.main()
