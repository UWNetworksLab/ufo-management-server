"""User page module functionality for getting elements for testing."""
from base_driver import BaseDriver
from sidebar import Sidebar

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class UserPage(BaseDriver):

  """User page action methods and locators."""

  ADD_USERS_LINK = (By.ID, 'add_users')


  def GetAddUserLink(self):
    return WebDriverWait(self.driver, 10).until(
        EC.visibility_of_element_located(((self.ADD_USERS_LINK))))

  def GetSidebar(self):
    return self.driver.find_element(*Sidebar.SIDEBAR)
