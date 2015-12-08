import unittest

from login_page import DevServerLoginPage
from landing_page import LandingPage

from selenium import webdriver


class LandingPageTest(unittest.TestCase):

  def setUp(self):
	self.driver = webdriver.Chrome('/usr/local/bin/chromedriver')
	DevServerLoginPage(self.driver).Login()

  def testLandingPage(self):
  	title = 'UfO Management Server'
  	instruction = ('Click one of the links on the side to login and '
  				   'administer the server.')

	self.driver.get('http://localhost:9999')

	landing_page = LandingPage(self.driver)
	self.assertEquals(title, landing_page.GetTitle().text)
	self.assertEquals(instruction, landing_page.GetInstruction().text)
	self.assertIsNotNone(landing_page.GetSidebar())


  def tearDown(self):
    self.driver.quit()


if __name__ == '__main__':
  unittest.main()
