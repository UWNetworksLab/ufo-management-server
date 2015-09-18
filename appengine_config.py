"""Custom configurations for Google App Engine."""

import os
import jinja2

from google.appengine.ext import vendor


ROOT = os.path.dirname(__file__)

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(ROOT),
    extensions=['jinja2.ext.autoescape',
                'jinja2.ext.i18n'],
    autoescape=True)


# Add any libraries installed in the "lib" folder.
vendor.add('lib')
