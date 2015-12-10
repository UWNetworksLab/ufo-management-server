import unittest

from base_test import BaseTest
from login_page import LoginPage
from landing_page import LandingPage
from test_config import CHROME_DRIVER_LOCATION

from selenium import webdriver


class LandingPageTest(BaseTest):

  def setUp(self):
    """Setup for test methods."""
    self.driver = webdriver.Chrome(CHROME_DRIVER_LOCATION)
    LoginPage(self.driver).Login(self.args)

  def testLandingPage(self):
    """Test the landing page."""
    title = 'UfO Management Server'
    instruction = ('Click one of the links on the side to login and '
                   'administer the server.')

    self.driver.get(self.args.server_url)

    landing_page = LandingPage(self.driver)
    self.assertEquals(title, landing_page.GetTitle().text)
    self.assertEquals(instruction, landing_page.GetInstruction().text)
    self.assertIsNotNone(landing_page.GetSidebar())

  def tearDown(self):
    """Teardown for test methods."""
    self.driver.quit()


if __name__ == '__main__':
  unittest.main()
