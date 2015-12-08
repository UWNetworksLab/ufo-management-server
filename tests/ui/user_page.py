from base_driver import BaseDriver
from sidebar import Sidebar

from selenium.webdriver.common.by import By

class UserPage(BaseDriver):
  """User page action methods and locators."""

  ADD_USERS_LINK = (By.ID, 'add_users')
  LIST_TOKENS_LINK = (By.ID, 'list_tokens')


  def GetAddUserLink(self):
    return self.driver.find_element(*self.ADD_USERS_LINK)

  def GetListTokensLink(self):
    return self.driver.find_element(*self.LIST_TOKENS_LINK)

  def GetSidebar(self):
    return self.driver.find_element(*Sidebar.SIDEBAR)
