import unittest

from base_test import BaseTest
from login_page import LoginPage
from sidebar import Sidebar
from test_config import CHROME_DRIVER_LOCATION

from selenium import webdriver


class SidebarTest(BaseTest):

  """Test sidebar partial page functionality."""

  def setUp(self):
    """Setup for test methods."""
    self.driver = webdriver.Chrome(CHROME_DRIVER_LOCATION)
    LoginPage(self.driver).Login(self.args)

  def testLinks(self):
    """Make sure all the links are pointed to the correct paths."""
    sidebar = Sidebar(self.driver)
    home_link = sidebar.GetLink(sidebar.HOME_LINK)
    # TODO: Make the path to be importable.
    self.assertEquals('/', home_link.get_attribute('data-href'))

    users_link = sidebar.GetLink(sidebar.USERS_LINK)
    self.assertEquals('/user', users_link.get_attribute('data-href'))

    proxy_servers_link = sidebar.GetLink(sidebar.PROXY_SERVERS_LINK)
    self.assertEquals('/proxyserver/list', proxy_servers_link.get_attribute('data-href'))

    setup_link = sidebar.GetLink(sidebar.SETUP_LINK)
    self.assertEquals('/setup', setup_link.get_attribute('data-href'))

    logout_link = sidebar.GetLink(sidebar.LOGOUT_LINK)
    self.assertEquals('/logout', logout_link.get_attribute('data-href'))

  def tearDown(self):
    """Teardown for test methods."""
    self.driver.quit()


if __name__ == '__main__':
  unittest.main()
