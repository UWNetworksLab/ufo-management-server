"""Test the logout module."""
from mock import patch

import unittest
import webtest
import logout


class LogoutTest(unittest.TestCase):

  """Test logout module functionality."""

  def setUp(self):
    self.testapp = webtest.TestApp(logout.APP)

  @patch('google.appengine.api.users.create_logout_url')
  def testLogoutHandler(self, mock_create_url):
    logout_relative_path = '/logout'
    fake_redirect_url = 'foo/bar'
    mock_create_url.return_value = fake_redirect_url

    response = self.testapp.get(logout_relative_path)

    mock_create_url.assert_called_once_with(logout.LOG_BACK_IN_PATH)
    self.assertEqual(response.status_int, 302)
    self.assertTrue(fake_redirect_url in response.location)


if __name__ == '__main__':
  unittest.main()
