"""Configs for the ui tests."""

# Hack to make the app directory to be visible here.
import sys
sys.path.append('../..')

import config

CHROME_DRIVER_LOCATION = '../../lib/chromedriver'
PATHS = config.PATHS
