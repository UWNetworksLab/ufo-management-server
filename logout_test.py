from mock import MagicMock
from mock import patch
import sys

from datastore import User
from datastore import OAuth

import unittest
import webapp2
import webtest
import logout


class LogoutTest(unittest.TestCase):

  def setUp(self):
    self.testapp = webtest.TestApp(logout.app)

  @patch('google.appengine.api.users.create_logout_url')
  def testLogoutHandler(self, mock_create_url):
    inputUrl = '/logout'
    fullUrl = 'http://localhost' + inputUrl
    fakeUrl = 'foo/bar'
    mock_create_url.return_value = fakeUrl

    response = self.testapp.get(inputUrl)
    
    mock_create_url.assert_called_once_with(fullUrl)
    self.assertEqual(response.status_int, 302)
    self.assertTrue(fakeUrl in response.location)


if __name__ == '__main__':
    unittest.main()
