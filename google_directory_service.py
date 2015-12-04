"""Module to interact with Google Directory API."""

from googleapiclient.discovery import build


MY_CUSTOMER_ALIAS = 'my_customer'

NUM_RETRIES = 3

# TODO(eholder): Write tests for these functions.

class GoogleDirectoryService(object):
  """Interact with Google Directory API."""

  def __init__(self, oauth_decorator):
    self.service = build(serviceName='admin',
                         version='directory_v1',
                         http=oauth_decorator.http())

  def GetUsers(self):
    """Get the users of a customer account.

    Returns:
      users: A list of users.
    """
    users = []
    page_token = ''
    while True:
      request = self.service.users().list(customer=MY_CUSTOMER_ALIAS,
                                          maxResults=500,
                                          pageToken=page_token,
                                          projection='full',
                                          orderBy='email')
      result = request.execute(num_retries=NUM_RETRIES)
      users += result['users']
      if 'nextPageToken' in result:
        page_token = result['nextPageToken']
      else:
        break

    return users

  def GetUsersByGroupKey(self, group_key):
    """Get the users belonging to a group in a customer account.

    Args:
      group_key: A string identifying a google group for querying users.

    Returns:
      users: A list of group members which are users and not groups.
    """
    users = []
    members = []
    page_token = ''
    while True:
      if page_token is '':
        request = self.service.members().list(groupKey=group_key)
      else:
        request = self.service.members().list(groupKey=group_key,
                                              pageToken=page_token)
      result = request.execute(num_retries=NUM_RETRIES)
      members += result['members']
      if 'nextPageToken' in result:
        page_token = result['nextPageToken']
      else:
        break

    user = 'USER'
    # Limit to only users, not groups
    for member in members:
      if 'type' in member and member['type'] == user:
        users.append(member)

    return users

  def SearchForUser(self, user_key):
    """Search for a user based on a user key.

    Args:
      user_key: A string identifying an individual user.

    Returns:
      users: A list with that user in it or empty.
      List format is used here for consistency with the other methods.
    """
    users = []
    request = self.service.users().get(userKey=user_key, projection='full')
    result = request.execute(num_retries=NUM_RETRIES)
    if result['primaryEmail']:
      users.append(result)

    return users

