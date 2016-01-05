"""Custom configurations for Google App Engine."""

from config import PATHS
from google.appengine.api import app_identity
from google.appengine.ext import vendor
import jinja2
import os
import xsrf


ROOT = os.path.dirname(__file__)

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(ROOT),
    extensions=['jinja2.ext.autoescape',
                'jinja2.ext.i18n'],
    autoescape=True)


JINJA_ENVIRONMENT.globals['xsrf_token'] = xsrf.XSRFToken()
HOST = str(app_identity.get_default_version_hostname())
JINJA_ENVIRONMENT.globals['BASE_URL'] = ('https://' + HOST)
JINJA_ENVIRONMENT.globals['EMAIL_VALIDATION_PATTERN'] = r'[^@]+@[^@]+.[^@]+'
email_validation_error = 'Please supply a valid email address.'
JINJA_ENVIRONMENT.globals['EMAIL_VALIDATION_ERROR'] = email_validation_error
# Key lookup for users and group allows email or unique id.
key_lookup_pattern = r'([^@]+@[^@]+.[^@]+|[a-zA-Z0-9]+)'
key_lookup_error = 'Please supply a valid email address or unique id.'
JINJA_ENVIRONMENT.globals['KEY_LOOKUP_VALIDATION_PATTERN'] = key_lookup_pattern
JINJA_ENVIRONMENT.globals['KEY_LOOKUP_VALIDATION_ERROR'] = key_lookup_error

for key, value in PATHS.iteritems():
  JINJA_ENVIRONMENT.globals[key] = value

# Add any libraries installed in the "lib" folder.
vendor.add('lib')
