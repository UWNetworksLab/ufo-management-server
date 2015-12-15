"""Configs for the ui tests."""

# Hack to make the app directory to be visible here.
import sys
sys.path.append('../..')

# pylint: disable=unused-import
from config import PATHS

CHROME_DRIVER_LOCATION = '../../lib/chromedriver'
