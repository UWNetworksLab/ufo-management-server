import argparse
import sys
import unittest

from landing_page_test import LandingPageTest
from sidebar_test import SidebarTest
from user_page_test import UserPageTest


def _ParseArgs():
  """Parse the arguments from the commandline."""
  parser = argparse.ArgumentParser()
  parser.add_argument('--server_url', action='store',
                      dest='server_url', default=None,
                      help='URL of the server to test.')
  parser.add_argument('--email', action='store',
                      dest='email', default=None,
                      help='Email of the user to login.')
  parser.add_argument('--password', action='store',
                      dest='password', default=None,
                      help='Password of the user to login.')
  return parser.parse_args()

def MakeSuite(testcase_class):
  """Add the test cases into suites."""
  testloader = unittest.TestLoader()
  testnames = testloader.getTestCaseNames(testcase_class)
  suite = unittest.TestSuite()
  for name in testnames:
    suite.addTest(testcase_class(name, args=_ParseArgs()))
  return suite

suite = unittest.TestSuite()
suite.addTest(MakeSuite(LandingPageTest))
suite.addTest(MakeSuite(UserPageTest))
suite.addTest(MakeSuite(SidebarTest))

unittest.TextTestRunner().run(suite)
