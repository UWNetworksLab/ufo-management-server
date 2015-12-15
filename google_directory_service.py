"""Module to interact with Google Directory API."""

from datastore import NotificationChannel
from googleapiclient.discovery import build
from time import time


MY_CUSTOMER_ALIAS = 'my_customer'

NUM_RETRIES = 3

VALID_WATCH_EVENTS = ['add', 'delete', 'makeAdmin', 'undelete', 'update']

# TODO(eholder): Write tests for these functions.

class GoogleDirectoryService(object):

  """Interact with Google Directory API."""

  def __init__(self, oauth_decorator):
    """Create a service object for admin directory services using oauth."""
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
      if 'type' in member and member['type'] == user and member['id']:
        users.append(self.GetUser(member['id']))

    return users

  def GetUser(self, user_key):
    """Get a user based on a user key.

    Args:
      user_key: A string identifying an individual user.

    Returns:
      users: The user if found.
    """
    request = self.service.users().get(userKey=user_key, projection='full')
    result = request.execute(num_retries=NUM_RETRIES)

    return result

  def GetUserAsList(self, user_key):
    """Get a user based on a user key.

    List format is used here for consistency with the other methods and to
    simplify rendering a template based on the response.

    Args:
      user_key: A string identifying an individual user.

    Returns:
      users: A list with that user in it or empty.
    """
    users = []
    result = self.GetUser(user_key)
    if result['primaryEmail']:
      users.append(result)

    return users

  def IsAdminUser(self, user_key):
    """Check if a given user is an admin according to the directory API.

    Args:
      user_key: A string identifying an individual user.

    Returns:
      True or false for whether or not the user is or is not an admin.
    """
    result = self.GetUser(user_key)
    return result['isAdmin']

  def WatchUsers(self, event):
    """Subscribe to notifications for users with a specific event.

    Args:
      event: The event to subsribe to notifications for.
    """
    # Don't subscribe if the event isn't valid.
    if event not in VALID_WATCH_EVENTS:
      return

    # Don't subscribe if we have already subscribed.
    channels = NotificationChannel.GetAll()
    for channel in channels:
      if channel.event == event:
        return

    time_in_millis = str(int(round(time() * 1000)))
    id_field = MY_CUSTOMER_ALIAS + '_' + event + '_' + time_in_millis
    body = {}
    body['id'] = id_field
    body['type'] = 'web_hook'
    address = 'https://ufo-management-server-ethan.appspot.com/receive'
    body['address'] = address
    request = self.service.users().watch(customer=MY_CUSTOMER_ALIAS,
                                         event=event,
                                         projection='full',
                                         orderBy='email',
                                         body=body)
    result = request.execute(num_retries=NUM_RETRIES)

    if 'resourceId' in result:
      NotificationChannel.Insert(event=event, channel_id=id_field,
                                  resource_id=result['resourceId'])

  def StopNotifications(self, notification_channel):
    """Unsubscribe from notifications for a given notification channel.

    Args:
      notification_channel: A NotificationChannel datastore entity to unsub.
    """
    body = {}
    body['id'] = notification_channel.channel_id
    body['resourceId'] = notification_channel.resource_id
    request = self.service.channels().stop(body=body)
    request.execute(num_retries=NUM_RETRIES)

    NotificationChannel.Delete(notification_channel.key.id)

