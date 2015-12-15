"""Base driver module to inherit from."""

class BaseDriver(object):

  """Base driver that will be called from all pages and elements."""

  # pylint: disable=too-few-public-methods

  def __init__(self, driver):
    """Create the base driver object."""
    self.driver = driver
