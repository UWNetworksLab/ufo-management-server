import unittest

from login_page import DevServerLoginPage
from sidebar import Sidebar
from test_config import CHROME_DRIVER_LOCATION
from user_page import UserPage

from selenium import webdriver


class SidebarTest(unittest.TestCase):

  def setUp(self):
    self.driver = webdriver.Chrome(CHROME_DRIVER_LOCATION)
    DevServerLoginPage(self.driver).Login()

  def testLinks(self):
    sidebar = Sidebar(self.driver)
    home_link = sidebar.GetLink(sidebar.HOME_LINK)
    # TODO: Make the path to be importable.
    self.assertEquals('/', home_link.get_attribute('data-href'))

    users_link = sidebar.GetLink(sidebar.USERS_LINK)
    self.assertEquals('/user', users_link.get_attribute('data-href'))

    tokens_link = sidebar.GetLink(sidebar.TOKENS_LINK)
    self.assertEquals('/user/listTokens', tokens_link.get_attribute('data-href'))

    proxy_servers_link = sidebar.GetLink(sidebar.PROXY_SERVERS_LINK)
    self.assertEquals('/proxyserver/list', proxy_servers_link.get_attribute('data-href'))
  
    setup_link = sidebar.GetLink(sidebar.SETUP_LINK)
    self.assertEquals('/setup/oauthclient', setup_link.get_attribute('data-href'))

    logout_link = sidebar.GetLink(sidebar.LOGOUT_LINK)
    self.assertEquals('/logout', logout_link.get_attribute('data-href'))

  def tearDown(self):
    self.driver.quit()


if __name__ == '__main__':
  unittest.main()
