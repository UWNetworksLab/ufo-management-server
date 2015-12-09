"""XSRF protection for authenticated users.

Note that this module is simple and should only be used in this specific
project. For a more robust XSRF protection implementation, please see
https://github.com/cyberphobia/xsrfutil/blob/master/xsrfutil.py
"""

import base64
import binascii
import hmac
import logging
import os

from google.appengine.api import memcache
from google.appengine.api import users
from google.appengine.ext import ndb


def XSRFToken():
  """Generate a new xsrf secret and output it in urlsafe base64 encoding."""
  digester = hmac.new(str(XsrfSecret.get()))
  digester.update(str(users.get_current_user().user_id()))
  return base64.urlsafe_b64encode(digester.digest())


def XSRFProtect(func):
  """Decorator to require valid XSRF token."""
  def decorate(self, *args, **kwargs):
    """Actual decorate function that requires a valid XSRF token.

    Args:
      args: Parameters passed on to the specified function if successful.
      kwargs: Parameters passed on to the specified function if successful.
    """
    token = self.request.get('xsrf', None)
    if not token:
      logging.error('xsrf token not included')
      self.abort(403)
    if not ConstTimeCompare(token, XSRFToken()):
      logging.error('xsrf token does not validate')
      self.abort(403)
    return func(self, *args, **kwargs)

  return decorate


def ConstTimeCompare(string_a, string_b):
  """Compare the the given strings in constant time."""
  if len(string_a) != len(string_b):
    return False

  equals = 0
  for char_x, char_y in zip(string_a, string_b):
    equals |= ord(char_x) ^ ord(char_y)

  return equals == 0


class XsrfSecret(ndb.Model):

  """Model for datastore to store the XSRF secret."""

  # pylint: disable=too-few-public-methods
  secret = ndb.StringProperty(required=True)

  @staticmethod
  def get():
    """Retrieve the XSRF secret.

    Tries to retrieve the XSRF secret from memcache, and if that fails, falls
    back to getting it out of datastore. Note that the secret should not be
    changed, as that would result in all issued tokens becoming invalid.

    Returns:
      A unicode object of the secret.
    """
    secret = memcache.get('xsrf_secret')
    if not secret:
      xsrf_secret = XsrfSecret.query().get()
      if not xsrf_secret:
        # hmm, nothing found? We need to generate a secret for xsrf protection.
        secret = binascii.b2a_hex(os.urandom(16))
        xsrf_secret = XsrfSecret(secret=secret)
        xsrf_secret.put()

      secret = xsrf_secret.secret
      memcache.set('xsrf_secret', secret)

    return secret
