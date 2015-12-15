"""Sidebar module to get links for testing."""
from base_driver import BaseDriver

from selenium.webdriver.common.by import By

class Sidebar(BaseDriver):

  """Sidebar action methods and locators."""

  # pylint: disable=too-few-public-methods

  SIDEBAR = (By.TAG_NAME, 'ufo-sidebar')

  HOME_LINK = (By.ID, 'Home')
  USERS_LINK = (By.ID, 'Users')
  PROXY_SERVERS_LINK = (By.ID, 'Proxy Servers')
  SETUP_LINK = (By.ID, 'Setup')
  LOGOUT_LINK = (By.ID, 'Logout')


  def GetLink(self, link_locator):
    """Get an element in the sidebar based on the link locator given."""
    return self.driver.find_element(*link_locator)
