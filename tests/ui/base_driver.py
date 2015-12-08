class BaseDriver(object):
  """Base driver that will be called from all pages and elements."""

  def __init__(self, driver):
    self.driver = driver
