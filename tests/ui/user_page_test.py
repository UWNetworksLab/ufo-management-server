import unittest

from login_page import DevServerLoginPage
from test_config import CHROME_DRIVER_LOCATION
from user_page import UserPage

from selenium import webdriver


class UserPageTest(unittest.TestCase):

  def setUp(self):
    self.driver = webdriver.Chrome(CHROME_DRIVER_LOCATION)
    DevServerLoginPage(self.driver).Login()

  def testUserPage(self):
    add_users = (u'Add Users').upper()

    self.driver.get('http://localhost:9999/user')
    user_page = UserPage(self.driver)
    self.assertEquals(add_users, user_page.GetAddUserLink().text)
    self.assertIsNotNone(user_page.GetSidebar())

  def tearDown(self):
    self.driver.quit()


if __name__ == '__main__':
  unittest.main()
