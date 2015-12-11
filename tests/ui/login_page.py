from base_driver import BaseDriver

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait




class LoginPage(BaseDriver):
  """The Google login page (not the fake dev server login)."""

  # pylint: disable=too-few-public-methods

  EMAIL_INPUT = (By.ID, 'Email')
  NEXT_BUTTON = (By.ID, 'next')
  PASSWORD_INPUT = (By.ID, 'Passwd')
  SIGN_IN_BUTTON = (By.ID, 'signIn')
  APP_APPROVE_BUTTON = (By.ID, 'approve_button')
  OAUTH_SCOPES = (By.ID, 'scope_list')
  OAUTH_APPROVE_BUTTON = (By.ID, 'submit_approve_access')

  REMEMBER_APPROVAL_MESSAGE = 'Remember this approval for the next 30 days'

  def _IsElementPresent(self, locator):
    """Determine if element is present."""
    try:
      self.driver.find_element(*locator)
    except NoSuchElementException, e:
      return False
    return True

  def Login(self, args):
    """Go through the login and authorization flows."""
    self.driver.get(args.server_url + '/user')

    email_input = self.driver.find_element(*self.EMAIL_INPUT)
    email_input.send_keys(args.email)

    next_button = self.driver.find_element(*self.NEXT_BUTTON)
    next_button.click()

    password_input = WebDriverWait(self.driver, 10).until(
        EC.presence_of_element_located(((self.PASSWORD_INPUT))))
    password_input.send_keys(args.password)

    sign_in_button = self.driver.find_element(*self.SIGN_IN_BUTTON)
    sign_in_button.click()

    # App approval page.
    # This page will reappear every 30 days.
    if self.REMEMBER_APPROVAL_MESSAGE in self.driver.page_source:
      app_approve_button = self.driver.find_element(*self.APP_APPROVE_BUTTON)
      app_approve_button.click()

    # OAuth Page
    if self._IsElementPresent(self.OAUTH_SCOPES):
      oauth_approve_button = WebDriverWait(self.driver, 10).until(
          EC.element_to_be_clickable((self.OAUTH_APPROVE_BUTTON)))
      oauth_approve_button.click()
