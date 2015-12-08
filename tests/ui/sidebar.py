from base_driver import BaseDriver

from selenium.webdriver.common.by import By

class Sidebar(BaseDriver):
  """Sidebar action methods and locators."""

  SIDEBAR = (By.TAG_NAME, 'ufo-sidebar')

  HOME_LINK = (By.ID, 'Home')
  USERS_LINK = (By.ID, 'Users')
  TOKENS_LINK = (By.ID, 'Tokens')
  PROXY_SERVERS_LINK = (By.ID, 'Proxy Servers')
  SETUP_LINK = (By.ID, 'Setup')
  LOGOUT_LINK = (By.ID, 'Logout')


  def GetLink(self, link_locator):
    return self.driver.find_element(*link_locator)