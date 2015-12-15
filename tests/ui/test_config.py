"""Configs for the ui tests."""

# Hack to make the app directory to be visible here.
import sys
sys.path.append('../..')

# pylint: disable=unused-import
from config import LANDING_PAGE_PATH
from config import USER_ADD_PATH
from config import USER_DELETE_PATH
from config import USER_DETAILS_PATH
from config import USER_GET_INVITE_CODE_PATH
from config import USER_GET_NEW_KEY_PAIR_PATH
from config import USER_PAGE_PATH
from config import USER_TOGGLE_REVOKED_PATH

CHROME_DRIVER_LOCATION = '../../lib/chromedriver'
