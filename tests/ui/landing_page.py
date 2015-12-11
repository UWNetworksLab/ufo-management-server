"""Landing page module for testing."""
from base_driver import BaseDriver
from sidebar import Sidebar

from selenium.webdriver.common.by import By

class LandingPage(BaseDriver):

  """Home page action methods and locators."""

  TITLE = (By.TAG_NAME, 'h2')
  INSTRUCTION = (By.TAG_NAME, 'h4')

  def GetTitle(self):
    return self.driver.find_element(*self.TITLE)

  def GetInstruction(self):
    return self.driver.find_element(*self.INSTRUCTION)

  def GetSidebar(self):
    return self.driver.find_element(*Sidebar.SIDEBAR)
