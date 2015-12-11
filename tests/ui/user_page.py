"""User page module functionality for getting elements for testing."""
from base_driver import BaseDriver
from sidebar import Sidebar

from selenium.webdriver.common.by import By

class UserPage(BaseDriver):

  """User page action methods and locators."""

  ADD_USERS_LINK = (By.ID, 'add_users')


  def GetAddUserLink(self):
    return self.driver.find_element(*self.ADD_USERS_LINK)

  def GetSidebar(self):
    return self.driver.find_element(*Sidebar.SIDEBAR)
