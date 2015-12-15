"""Test user page module functionality."""
import unittest

from base_test import BaseTest
from login_page import LoginPage
from test_config import CHROME_DRIVER_LOCATION
from test_config import PATHS
from user_page import UserPage

from selenium import webdriver


class UserPageTest(BaseTest):

  """Test user page functionality."""

  def setUp(self):
    """Setup for test methods."""
    self.driver = webdriver.Chrome(CHROME_DRIVER_LOCATION)
    LoginPage(self.driver).Login(self.args)

  def testUserPage(self):
    """Test the user page."""
    add_users = (u'Add Users').upper()

    self.driver.get(self.args.server_url + PATHS['user_page_path'])
    user_page = UserPage(self.driver)
    self.assertEquals(add_users, user_page.GetAddUserLink().text)
    self.assertIsNotNone(user_page.GetSidebar())

  def tearDown(self):
    """Teardown for test methods."""
    self.driver.quit()


if __name__ == '__main__':
  unittest.main()
