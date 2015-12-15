"""Test the logout module."""
from mock import patch

from config import PATHS
import unittest
import webtest
import logout


class LogoutTest(unittest.TestCase):

  """Test logout module functionality."""

  def setUp(self):
    """Setup test app on which to call handlers."""
    self.testapp = webtest.TestApp(logout.APP)

  @patch('google.appengine.api.users.create_logout_url')
  def testLogoutHandler(self, mock_create_url):
    """Test that logging out works without auth.

    Also test that users can log back in without looping back through the
    logout flow.
    """
    fake_redirect_url = 'foo/bar'
    mock_create_url.return_value = fake_redirect_url

    response = self.testapp.get(PATHS['logout'])

    mock_create_url.assert_called_once_with(PATHS['user_page_path'])
    self.assertEqual(response.status_int, 302)
    self.assertTrue(fake_redirect_url in response.location)


if __name__ == '__main__':
  unittest.main()
