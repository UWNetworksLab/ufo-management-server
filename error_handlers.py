"""The error handling module."""

import logging

from oauth2client.client import FlowExchangeError


# pylint: disable=unused-argument
def Handle500(request, response, exception):
  if (isinstance(exception, FlowExchangeError)
      and exception.message == 'invalid_client'):
    response.write('Setup your client_secret in the datastore.')
  else:
    # TODO(henryc): Figure out a user-friendly way to handle general errors.
    logging.exception(exception)
    response.write('Unknown error has occurred.')
