"""Test google directory service module functionality."""

from appengine_config import JINJA_ENVIRONMENT
from config import PATHS
import google_directory_service
from google_directory_service import GoogleDirectoryService
from google_directory_service import MY_CUSTOMER_ALIAS
from google_directory_service import NUM_RETRIES
from google_directory_service import VALID_WATCH_EVENTS
from mock import MagicMock
from mock import patch
import unittest


def http():
  """Mock http function to return a mocked object."""
  return MOCK_HTTP


MOCK_HTTP = MagicMock()
MOCK_OAUTH_DECORATOR = MagicMock()
MOCK_OAUTH_DECORATOR.http = http
MOCK_SERVICE = MagicMock()

FAKE_EMAIL_1 = 'foo@mybusiness.com'
FAKE_EMAIL_2 = 'bar@mybusiness.com'
FAKE_USER_1 = {}
FAKE_USER_1['primaryEmail'] = FAKE_EMAIL_1
FAKE_USER_1['isAdmin'] = True
FAKE_USER_2 = {}
FAKE_USER_2['primaryEmail'] = FAKE_EMAIL_2
FAKE_USER_2['isAdmin'] = False
FAKE_USERS = [FAKE_USER_1, FAKE_USER_2]
FAKE_ID_1 = 'some id 1' # Also doubles as a user key
FAKE_ID_2 = 'some id 2'
FAKE_GROUP_MEMBER_USER_1 = {}
FAKE_GROUP_MEMBER_USER_1['type'] = 'USER'
FAKE_GROUP_MEMBER_USER_1['id'] = FAKE_ID_1
FAKE_GROUP_MEMBER_USER_2 = {}
FAKE_GROUP_MEMBER_USER_2['type'] = 'USER'
FAKE_GROUP_MEMBER_USER_2['id'] = FAKE_ID_2
FAKE_GROUP_MEMBER_GROUP = {}
FAKE_GROUP_MEMBER_GROUP['type'] = 'GROUP'
FAKE_GROUP = [FAKE_GROUP_MEMBER_USER_1, FAKE_GROUP_MEMBER_USER_2,
              FAKE_GROUP_MEMBER_GROUP]
FAKE_PAGE_TOKEN = 'I am a fake page token'
FAKE_GROUP_KEY = "my_group@mybusiness.com"


class GoogleDirectoryServiceTest(unittest.TestCase):

  """Test google directory service class functionality."""

  @patch('google_directory_service.build')
  def setUp(self, mock_build):
    """Setup test object on which to call methods later on."""
    mock_build.return_value = MOCK_SERVICE
    self.directory_service = GoogleDirectoryService(MOCK_OAUTH_DECORATOR)

  @patch('google_directory_service.build')
  def testInit(self, mock_build):
    """Test that init passes the correct parameters and creates an object."""
    fake_service = MagicMock()
    mock_build.return_value = fake_service
    google_directory_service = GoogleDirectoryService(MOCK_OAUTH_DECORATOR)
    mock_build.assert_called_once_with(serviceName='admin',
                                       version='directory_v1',
                                       http=MOCK_HTTP)
    self.assertEqual(google_directory_service.service, fake_service)

  def testConstantDefinitions(self):
    """Test the constants set in GoogleDirectoryService are as expected."""
    self.assertEqual(MY_CUSTOMER_ALIAS, 'my_customer')
    self.assertEqual(NUM_RETRIES, 3)
    allowed_watch_events = ['add', 'delete', 'makeAdmin', 'undelete', 'update']
    self.assertEqual(VALID_WATCH_EVENTS, allowed_watch_events)

  @patch.object(MOCK_SERVICE.users.list, 'execute')
  @patch.object(MOCK_SERVICE.users, 'list')
  @patch.object(MOCK_SERVICE, 'users')
  def testGetUsers(self, mock_users, mock_list, mock_execute):
    """Test the get users request handles a valid response correctly."""
    fake_dictionary = {}
    fake_dictionary['users'] = FAKE_USERS
    mock_execute.return_value = fake_dictionary
    mock_list.return_value.execute = mock_execute
    mock_users.return_value.list = mock_list
    self.directory_service.users = mock_users

    users_returned = self.directory_service.GetUsers()

    mock_users.assert_called_once_with()
    mock_list.assert_called_once_with(customer=MY_CUSTOMER_ALIAS,
                                      maxResults=500, pageToken='',
                                      projection='full', orderBy='email')
    mock_execute.assert_called_once_with(num_retries=NUM_RETRIES)
    self.assertEqual(users_returned, FAKE_USERS)

  @patch.object(MOCK_SERVICE.users.list, 'execute')
  @patch.object(MOCK_SERVICE.users, 'list')
  @patch.object(MOCK_SERVICE, 'users')
  def testGetUsersPaged(self, mock_users, mock_list, mock_execute):
    """Test the get users request handles a long valid response correctly."""
    fake_dictionary_1 = {}
    fake_dictionary_1['users'] = FAKE_USERS
    fake_dictionary_1['nextPageToken'] = FAKE_PAGE_TOKEN
    fake_extra_user = MagicMock()
    fake_dictionary_2 = {}
    fake_dictionary_2['users'] = [fake_extra_user]
    expected_list = []
    expected_list += FAKE_USERS
    expected_list += [fake_extra_user]

    def SideEffect(customer, maxResults, pageToken, projection, orderBy):
      """Mock list function to return different mock execute calls."""
      # pylint: disable=unused-argument
      if pageToken == '':
        mock_execute.return_value = fake_dictionary_1
      else:
        mock_execute.return_value = fake_dictionary_2
      some_object = MagicMock()
      some_object.execute = mock_execute
      return some_object

    mock_list.side_effect = SideEffect
    mock_users.return_value.list = mock_list
    self.directory_service.users = mock_users

    users_returned = self.directory_service.GetUsers()

    mock_users.assert_any_call()
    mock_list.assert_any_call(customer=MY_CUSTOMER_ALIAS,
                              maxResults=500, pageToken='',
                              projection='full', orderBy='email')
    mock_list.assert_any_call(customer=MY_CUSTOMER_ALIAS,
                              maxResults=500, pageToken=FAKE_PAGE_TOKEN,
                              projection='full', orderBy='email')
    mock_execute.assert_any_call(num_retries=NUM_RETRIES)
    self.assertEqual(users_returned, expected_list)

  @patch.object(GoogleDirectoryService, 'GetUser')
  @patch.object(MOCK_SERVICE.members.list, 'execute')
  @patch.object(MOCK_SERVICE.members, 'list')
  @patch.object(MOCK_SERVICE, 'members')
  def testGetUsersByGroupKey(self, mock_members, mock_list, mock_execute,
                             mock_get_user):
    """Test get users by group key handles a valid response correctly."""
    fake_dictionary = {}
    fake_dictionary['members'] = FAKE_GROUP
    mock_execute.return_value = fake_dictionary
    mock_list.return_value.execute = mock_execute
    mock_members.return_value.list = mock_list
    self.directory_service.users = mock_members
    expected_list = [FAKE_GROUP_MEMBER_USER_1, FAKE_GROUP_MEMBER_USER_2]

    def SideEffect(user_key):
      """Mock get user function to return different users after group get."""
      if user_key == FAKE_ID_1:
        return FAKE_GROUP_MEMBER_USER_1
      else:
        return FAKE_GROUP_MEMBER_USER_2

    mock_get_user.side_effect = SideEffect

    users_returned = self.directory_service.GetUsersByGroupKey(FAKE_GROUP_KEY)

    mock_members.assert_called_once_with()
    mock_list.assert_called_once_with(groupKey=FAKE_GROUP_KEY)
    mock_execute.assert_called_once_with(num_retries=NUM_RETRIES)
    self.assertEqual(users_returned, expected_list)

  @patch.object(GoogleDirectoryService, 'GetUser')
  @patch.object(MOCK_SERVICE.members.list, 'execute')
  @patch.object(MOCK_SERVICE.members, 'list')
  @patch.object(MOCK_SERVICE, 'members')
  def testGetUsersByGroupKeyPaged(self, mock_members, mock_list, mock_execute,
                                  mock_get_user):
    """Test get users by group key handles a long valid response correctly."""
    fake_dictionary_1 = {}
    fake_dictionary_1['members'] = FAKE_GROUP
    fake_dictionary_1['nextPageToken'] = FAKE_PAGE_TOKEN
    fake_dictionary_2 = {}
    fake_dictionary_2['members'] = FAKE_GROUP
    expected_list = [FAKE_GROUP_MEMBER_USER_1, FAKE_GROUP_MEMBER_USER_2,
                     FAKE_GROUP_MEMBER_USER_1, FAKE_GROUP_MEMBER_USER_2]

    def SideEffect1(groupKey, pageToken=''):
      """Mock list function to return different mock execute calls."""
      # pylint: disable=unused-argument
      if pageToken == '':
        mock_execute.return_value = fake_dictionary_1
      else:
        mock_execute.return_value = fake_dictionary_2
      some_object = MagicMock()
      some_object.execute = mock_execute
      return some_object

    mock_list.side_effect = SideEffect1
    mock_members.return_value.list = mock_list
    self.directory_service.users = mock_members

    def SideEffect2(user_key):
      """Mock get user function to return different users after group get."""
      if user_key == FAKE_ID_1:
        return FAKE_GROUP_MEMBER_USER_1
      else:
        return FAKE_GROUP_MEMBER_USER_2

    mock_get_user.side_effect = SideEffect2

    users_returned = self.directory_service.GetUsersByGroupKey(FAKE_GROUP_KEY)

    mock_members.assert_any_call()
    mock_list.assert_any_call(groupKey=FAKE_GROUP_KEY)
    mock_list.assert_any_call(groupKey=FAKE_GROUP_KEY,
                              pageToken=FAKE_PAGE_TOKEN)
    mock_execute.assert_any_call(num_retries=NUM_RETRIES)
    self.assertEqual(users_returned, expected_list)

  @patch.object(MOCK_SERVICE.users.get, 'execute')
  @patch.object(MOCK_SERVICE.users, 'get')
  @patch.object(MOCK_SERVICE, 'users')
  def testGetUser(self, mock_users, mock_get, mock_execute):
    """Test the get user request handles a valid response correctly."""
    mock_execute.return_value = FAKE_USER_1
    mock_get.return_value.execute = mock_execute
    mock_users.return_value.get = mock_get
    self.directory_service.users = mock_users

    user_returned = self.directory_service.GetUser(FAKE_ID_1)

    mock_users.assert_called_once_with()
    mock_get.assert_called_once_with(userKey=FAKE_ID_1, projection='full')
    mock_execute.assert_called_once_with(num_retries=NUM_RETRIES)
    self.assertEqual(user_returned, FAKE_USER_1)

  @patch.object(GoogleDirectoryService, 'GetUser')
  def testGetUserAsList(self, mock_get_user):
    """Test get user as list turns a valid response into a list."""
    mock_get_user.return_value = FAKE_USER_1

    user_list_returned = self.directory_service.GetUserAsList(FAKE_ID_1)

    mock_get_user.assert_called_once_with(FAKE_ID_1)
    self.assertEqual(user_list_returned, [FAKE_USER_1])

  @patch.object(GoogleDirectoryService, 'GetUser')
  def testIsAdminUser(self, mock_get_user):
    """Test is admin user returns whether a user is an admin."""

    def SideEffect(user_key):
      """Mock get user function to return different users based on key."""
      if user_key == FAKE_ID_1:
        return FAKE_USER_1
      else:
        return FAKE_USER_2

    mock_get_user.side_effect = SideEffect

    boolean_returned = self.directory_service.IsAdminUser(FAKE_ID_1)

    mock_get_user.assert_called_with(FAKE_ID_1)
    self.assertEqual(boolean_returned, True)

    boolean_returned = self.directory_service.IsAdminUser(FAKE_ID_2)

    mock_get_user.assert_called_with(FAKE_ID_2)
    self.assertEqual(boolean_returned, False)

  @patch('datastore.NotificationChannel.Insert')
  @patch.object(MOCK_SERVICE.users.watch, 'execute')
  @patch.object(MOCK_SERVICE.users, 'watch')
  @patch.object(MOCK_SERVICE, 'users')
  @patch('google_directory_service.time')
  @patch('datastore.NotificationChannel.GetAll')
  def testWatchUsers(self, mock_get_all, mock_time, mock_users, mock_watch,
                     mock_execute, mock_insert):
    """Test watch users requests a channel then inserts into the datastore."""
    fake_resource_id = 'some resource id'
    fake_watch_result = {}
    fake_watch_result['resourceId'] = fake_resource_id
    mock_execute.return_value = fake_watch_result
    mock_watch.return_value.execute = mock_execute
    mock_users.return_value.watch = mock_watch
    self.directory_service.users = mock_users

    fake_time = 1.001
    fake_time_in_millis = '1001'
    mock_time.return_value = fake_time
    invalid_event = 'foo'
    fake_event_already_watched = 'add'
    fake_event_not_watched = 'delete'
    fake_channel = MagicMock(event=fake_event_already_watched)
    mock_get_all.return_value = [fake_channel]

    # Test with an invalid event, which should just return.
    self.directory_service.WatchUsers(invalid_event)

    mock_get_all.assert_not_called()
    mock_time.assert_not_called()
    mock_users.assert_not_called()
    mock_watch.assert_not_called()
    mock_execute.assert_not_called()
    mock_insert.assert_not_called()

    # Test with an event already in the datastore, which should just return.
    self.directory_service.WatchUsers(fake_event_already_watched)

    mock_get_all.assert_any_call()
    mock_time.assert_not_called()
    mock_users.assert_not_called()
    mock_watch.assert_not_called()
    mock_execute.assert_not_called()
    mock_insert.assert_not_called()

    # Test with an event not in the datastore, which should flow through.
    self.directory_service.WatchUsers(fake_event_not_watched)

    fake_body = {}
    fake_body['id'] = (MY_CUSTOMER_ALIAS + '_' + fake_event_not_watched + '_' +
                       fake_time_in_millis)
    fake_body['type'] = 'web_hook'
    fake_address = (JINJA_ENVIRONMENT.globals['BASE_URL'] +
                    PATHS['receive_push_notifications'])
    fake_body['address'] = fake_address

    mock_get_all.assert_any_call()
    mock_time.assert_called_once_with()
    mock_users.assert_called_once_with()
    mock_watch.assert_called_once_with(customer=MY_CUSTOMER_ALIAS,
                                       event=fake_event_not_watched,
                                       projection='full', orderBy='email',
                                       body=fake_body)
    mock_execute.assert_called_once_with(num_retries=NUM_RETRIES)
    mock_insert.assert_called_once_with(event=fake_event_not_watched,
                                        channel_id=fake_body['id'],
                                        resource_id=fake_resource_id)

  @patch('datastore.NotificationChannel.Delete')
  @patch.object(MOCK_SERVICE.channels.stop, 'execute')
  @patch.object(MOCK_SERVICE.channels, 'stop')
  @patch.object(MOCK_SERVICE, 'channels')
  def testStopNotifications(self, mock_channels, mock_stop, mock_execute,
                            mock_delete):
    """Test stop notifications requests with stop then deletes the channel."""
    fake_id = 'foobarbaz'
    fake_key = MagicMock(id=fake_id)
    fake_channel_id = 'some channel id'
    fake_resource_id = 'some resource id'
    fake_notification_channel = MagicMock(channel_id=fake_channel_id,
                                          resource_id=fake_resource_id,
                                          key=fake_key)
    fake_body = {}
    fake_body['id'] = fake_channel_id
    fake_body['resourceId'] = fake_resource_id
    mock_stop.return_value.execute = mock_execute
    mock_channels.return_value.stop = mock_stop
    self.directory_service.channels = mock_channels

    self.directory_service.StopNotifications(fake_notification_channel)

    mock_channels.assert_called_once_with()
    mock_stop.assert_called_once_with(body=fake_body)
    mock_execute.assert_called_once_with(num_retries=NUM_RETRIES)
    mock_delete.assert_called_once_with(fake_id)

if __name__ == '__main__':
  unittest.main()
