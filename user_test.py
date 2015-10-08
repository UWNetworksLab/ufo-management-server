from mock import MagicMock
from mock import patch
import sys

from datastore import User

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
RENDER_TEMPLATE = '_RenderUserListTemplate'


class UserTest(unittest.TestCase):

  def setUp(self):
    app = webapp2.WSGIApplication([
        ('/', user.ListUsersHandler),
        ('/user/delete', user.DeleteUserHandler),
    ])
    self.testapp = webtest.TestApp(app)

  def testListUsersHandler(self):
    with patch.object(user, RENDER_TEMPLATE) as mock_render_template:
      self.testapp.get('/')
      mock_render_template.assert_called_once_with()

  def testDeleteUserHandler(self):
    with patch.object(user.User, 'DeleteUser') as mock_delete_user:
      with patch.object(user, RENDER_TEMPLATE) as mock_render_template:
        self.testapp.get('/user/delete?email=%s' % FAKE_EMAIL)
        mock_delete_user.assert_called_once_with(FAKE_EMAIL)
        mock_render_template.assert_called_once_with()

  def testRenderUserListTemplate(self):
    fake_user = User(email=FAKE_EMAIL, name=FAKE_NAME)
    fake_users = [fake_user]
    with patch.object(user.User, 'GetUsers') as mock_get_users:
      mock_get_users.return_value = fake_users
      user_list_template = user._RenderUserListTemplate()
      self.assertTrue('list tokens' in user_list_template)
      self.assertTrue(
          ('user/delete?email=' + fake_user.email) in user_list_template)
      self.assertTrue(
          ('token/add?email=' + fake_user.email) in user_list_template)


if __name__ == '__main__':
    unittest.main()
