from base_driver import BaseDriver

from selenium.webdriver.common.by import By


class DevServerLoginPage(BaseDriver):
  """Login page action methods and locators."""

  EMAIL_INPUT = (By.ID, 'email')
  ADMIN_CHECKBOX = (By.ID, 'admin')
  LOGIN_BUTTON = (By.ID, 'submit-login')


  def Login(self):
    self.driver.get('http://localhost:9999/user')

    email_input = self.driver.find_element(*self.EMAIL_INPUT)
    email_input.clear()
    email_input.send_keys('henry@henrychang.mygbiz.com')

    admin_checkbox = self.driver.find_element(*self.ADMIN_CHECKBOX)
    admin_checkbox.click()

    login_button = self.driver.find_element(*self.LOGIN_BUTTON)
    login_button.click()
