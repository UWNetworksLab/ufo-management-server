"""Test base module functionality."""

import unittest

class BaseTest(unittest.TestCase):

  """Base test class to inherit from."""

  def __init__(self, methodName='runTest', args=None):
    """Create the base test object for others to inherit."""
    super(BaseTest, self).__init__(methodName)
    self.args = args
