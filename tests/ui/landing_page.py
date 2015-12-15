"""Landing page module for testing."""
from base_driver import BaseDriver
from sidebar import Sidebar

from selenium.webdriver.common.by import By

class LandingPage(BaseDriver):

  """Home page action methods and locators."""

  TITLE = (By.TAG_NAME, 'h2')
  INSTRUCTION = (By.TAG_NAME, 'h4')

  def GetTitle(self):
    """Get the title element on the landing page."""
    return self.driver.find_element(*self.TITLE)

  def GetInstruction(self):
    """Get the instructions element on the landing page."""
    return self.driver.find_element(*self.INSTRUCTION)

  def GetSidebar(self):
    """Get the sidebar element on the landing page."""
    return self.driver.find_element(*Sidebar.SIDEBAR)
