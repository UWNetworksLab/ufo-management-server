import unittest

from login_page import DevServerLoginPage
from user_page import UserPage

from selenium import webdriver


class UserPageTest(unittest.TestCase):

  def setUp(self):
  self.driver = webdriver.Chrome('../../chromedriver')
  DevServerLoginPage(self.driver).Login()

  def testUserPage(self):
    add_users = 'Add Users'
    list_tokens = 'List Tokens'

    self.driver.get('http://localhost:9999/user')
  user_page = UserPage(self.driver)
  self.assertEquals(add_users, user_page.GetAddUserLink().text)
  self.assertEquals(list_tokens, user_page.GetListTokensLink().text)
  self.assertIsNotNone(user_page.GetSidebar())

  def tearDown(self):
    self.driver.quit()


if __name__ == '__main__':
  unittest.main()
