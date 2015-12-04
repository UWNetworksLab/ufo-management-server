"""The error handling module."""

import logging

from oauth2client.client import FlowExchangeError


# pylint: disable=unused-argument
def Handle500(request, response, exception):
  """Handle status 500 http request errors generically.

  Args:
    request: The request that generated a status 500.
    response: The response object to write to or redirect on.
    exception: The specific exception caused by the request.
  """

  if (isinstance(exception, FlowExchangeError)
      and exception.message == 'invalid_client'):
    response.write('Setup your client_secret in the datastore.')
  else:
    # TODO(henryc): Figure out a user-friendly way to handle general errors.
    # TODO(eholder): Add tests for this.
    logging.exception(exception)
    response.write('Unknown error has occurred: ' + exception.message)
