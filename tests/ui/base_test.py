import unittest

class BaseTest(unittest.TestCase):
  """Base test"""

  def __init__(self, methodName='runTest', args=None):
    super(BaseTest, self).__init__(methodName)
    self.args = args
 