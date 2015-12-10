import unittest

from base_test import BaseTest
from login_page import LoginPage
from test_config import CHROME_DRIVER_LOCATION
from user_page import UserPage

from selenium import webdriver


class UserPageTest(BaseTest):

  def setUp(self):
    """Setup for test methods."""
    self.driver = webdriver.Chrome(CHROME_DRIVER_LOCATION)
    LoginPage(self.driver).Login(self.args)

  def testUserPage(self):
    """Test the user page."""
    add_users = (u'Add Users').upper()
    list_tokens = (u'List Tokens').upper()

    self.driver.get(self.args.server_url + '/user')
    user_page = UserPage(self.driver)
    self.assertEquals(add_users, user_page.GetAddUserLink().text)
    self.assertEquals(list_tokens, user_page.GetListTokensLink().text)
    self.assertIsNotNone(user_page.GetSidebar())

  def tearDown(self):
    """Teardown for test methods."""
    self.driver.quit()


if __name__ == '__main__':
  unittest.main()
