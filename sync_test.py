"""Test sync module functionality."""
from mock import MagicMock
from mock import patch
import sys

from googleapiclient import errors
import json

import unittest
import webtest

# Need to mock the decorator at function definition time, i.e. when the module
# is loaded. http://stackoverflow.com/a/7667621/2830207
def NoOpDecorator(func):
  """Mock decorator that passes through any function for testing."""
  return func

MOCK_ADMIN = MagicMock()
MOCK_ADMIN.OAUTH_DECORATOR.oauth_required = NoOpDecorator
MOCK_ADMIN.RequireAppAndDomainAdmin = NoOpDecorator
sys.modules['admin'] = MOCK_ADMIN

import sync


FAKE_STATE = 'delete'
FAKE_NUMBER = '1000000'
FAKE_UUID = '123087632460958036'
FAKE_EMAIL = 'fake_email@example.com'
FAKE_EVENT = 'delete'
FAKE_CHANNEL_ID = 'foo customer_delete_time-in-millis'
FAKE_RESOURCE_ID = 'i am a fake resource id'


class UserTest(unittest.TestCase):

  """Test sync class functionality."""

  def setUp(self):
    """Setup test app on which to call handlers."""
    self.testapp = webtest.TestApp(sync.APP)

  def testConstants(self):
    """Test that the constants are as we expect."""
    self.assertEqual(sync.RECEIVE_NOTIFICATIONS_PATH, '/receive')
    self.assertEqual(sync.SYNC_RELATIVE_PATH, '/sync')
    self.assertEqual(sync.CHANNELS_PATH, sync.SYNC_RELATIVE_PATH + '/channels')
    self.assertEqual(sync.NOTIFICATIONS_PATH,
    	               sync.SYNC_RELATIVE_PATH + '/notifications')
    self.assertEqual(sync.WATCH_FOR_DELETION_PATH,
    	               sync.SYNC_RELATIVE_PATH + '/delete')
    self.assertEqual(sync.UNSUBSCRIBE_PATH,
    	               sync.SYNC_RELATIVE_PATH + '/unsubscribe')

  @patch('sync.Notification.Insert')
  def testPushNotificationHandler(self, mock_insert):
    """Test that push notifications trigger an insert in the datastore."""
    params = {}
    params['id'] = FAKE_UUID
    params['primaryEmail'] = FAKE_EMAIL
    json_body = json.dumps(params)
    headers = {}
    headers['X-Goog-Resource-State'] = FAKE_STATE
    headers['X-Goog-Message-Number'] = FAKE_NUMBER

    response = self.testapp.post(sync.RECEIVE_NOTIFICATIONS_PATH, json_body,
                                 headers)

    mock_insert.assert_called_once_with(state=FAKE_STATE, number=FAKE_NUMBER,
                                        uuid=FAKE_UUID, email=FAKE_EMAIL)
    self.assertEqual('Got a notification!' in response, True)

  def testDefaultPathHandler(self):
    """Test that the default path redirects to the notifications path."""
    response = self.testapp.get(sync.SYNC_RELATIVE_PATH)
    self.assertEqual(response.status_int, 302)
    self.assertEqual(sync.NOTIFICATIONS_PATH in response.location, True)

  @patch('sync._RenderChannelsListTemplate')
  def testListChannelsHandler(self, mock_channels_template):
    """Test that the channel handler calls to render the channels."""
    self.testapp.get(sync.CHANNELS_PATH)
    mock_channels_template.assert_called_once_with()

  @patch('sync._RenderNotificationsTemplate')
  def testListNotificationsHandler(self, mock_notifications_template):
    """Test that the notification handler calls to render the notifications."""
    self.testapp.get(sync.NOTIFICATIONS_PATH)
    mock_notifications_template.assert_called_once_with()

  @patch('sync.GoogleDirectoryService.WatchUsers')
  @patch('sync.GoogleDirectoryService.__init__')
  def testWatchUserDeleteHandler(self, mock_directory_service,
                                 mock_watch_users):
    """Test the watch user delete handler calls watch users with delete."""
    # pylint: disable=too-many-arguments
    mock_directory_service.return_value = None

    response = self.testapp.get(sync.WATCH_FOR_DELETION_PATH)

    mock_directory_service.assert_called_once_with(MOCK_ADMIN.OAUTH_DECORATOR)
    mock_watch_users.assert_called_once_with('delete')
    self.assertEqual(response.status_int, 302)
    self.assertEqual(sync.CHANNELS_PATH in response.location, True)

  @patch('sync.GoogleDirectoryService.WatchUsers')
  @patch('sync.GoogleDirectoryService.__init__')
  def testWatchUserDeleteException(self, mock_directory_service,
                                   mock_watch_users):
    """Test the we fail gracefully if directory service has an error."""
    # pylint: disable=too-many-arguments
    fake_status = '404'
    fake_response = MagicMock(status=fake_status)
    fake_content = b'some error content'
    fake_error = errors.HttpError(fake_response, fake_content)
    mock_directory_service.side_effect = fake_error

    response = self.testapp.get(sync.WATCH_FOR_DELETION_PATH)

    mock_directory_service.assert_called_once_with(MOCK_ADMIN.OAUTH_DECORATOR)
    mock_watch_users.assert_not_called()
    self.assertEqual('An error occurred: ' in response, True)

  @patch('sync.GoogleDirectoryService.StopNotifications')
  @patch('sync.GoogleDirectoryService.__init__')
  @patch('sync.NotificationChannels.Get')
  def testUnsubscribeHandler(self, mock_get_channel, mock_directory_service,
                             mock_stop_notifications):
    """Test the unsubscribe handler calls unsubscribe for the given channel."""
    # pylint: disable=too-many-arguments
    fake_channel = MagicMock()
    mock_get_channel.return_value = fake_channel
    mock_directory_service.return_value = None

    response = self.testapp.get(sync.UNSUBSCRIBE_PATH + '?id=%s' % FAKE_UUID)

    mock_get_channel.assert_called_once_with(int(FAKE_UUID))
    mock_directory_service.assert_called_once_with(MOCK_ADMIN.OAUTH_DECORATOR)
    mock_stop_notifications.assert_called_once_with(fake_channel)
    self.assertEqual(response.status_int, 302)
    self.assertEqual(sync.CHANNELS_PATH in response.location, True)

  @patch('sync.GoogleDirectoryService.StopNotifications')
  @patch('sync.GoogleDirectoryService.__init__')
  @patch('sync.NotificationChannels.Get')
  def testUnsubscribeException(self, mock_get_channel, mock_directory_service,
                               mock_stop_notifications):
    """Test the we fail gracefully if directory service has an error."""
    # pylint: disable=too-many-arguments
    fake_channel = MagicMock()
    mock_get_channel.return_value = fake_channel
    fake_status = '404'
    fake_response = MagicMock(status=fake_status)
    fake_content = b'some error content'
    fake_error = errors.HttpError(fake_response, fake_content)
    mock_directory_service.side_effect = fake_error

    response = self.testapp.get(sync.UNSUBSCRIBE_PATH + '?id=%s' % FAKE_UUID)

    mock_get_channel.assert_called_once_with(int(FAKE_UUID))
    mock_directory_service.assert_called_once_with(MOCK_ADMIN.OAUTH_DECORATOR)
    mock_stop_notifications.assert_not_called()
    self.assertEqual('An error occurred: ' in response, True)

  @patch('sync.Notification.GetAll')
  def testRenderNotifications(self, mock_get_all):
    """Test notifications from the datastore are rendered as in the html."""
    fake_notification = MagicMock(state=FAKE_STATE, number=FAKE_NUMBER,
                                  uuid=FAKE_UUID, email=FAKE_EMAIL)
    fake_notifications = [fake_notification]
    mock_get_all.return_value = fake_notifications

    notification_template = sync._RenderNotificationsTemplate()

    mock_get_all.assert_called_once_with()
    self.assertEquals('View Notification Channels' in notification_template,
                      True)
    self.assertEquals('Number' in notification_template, True)
    self.assertEquals('State' in notification_template, True)
    self.assertEquals('Id' in notification_template, True)
    self.assertEquals('Email' in notification_template, True)
    self.assertEquals(FAKE_NUMBER in notification_template, True)
    self.assertEquals(FAKE_STATE in notification_template, True)
    self.assertEquals(FAKE_UUID in notification_template, True)
    self.assertEquals(FAKE_EMAIL in notification_template, True)

  @patch('sync.NotificationChannels.GetAll')
  def testRenderChannels(self, mock_get_all):
    """Test channels from the datastore are rendered as in the html."""
    fake_channel = MagicMock(event=FAKE_EVENT, channel_id=FAKE_CHANNEL_ID,
                             resource_id=FAKE_RESOURCE_ID)
    fake_channels = [fake_channel]
    mock_get_all.return_value = fake_channels

    channels_template = sync._RenderChannelsListTemplate()

    mock_get_all.assert_called_once_with()
    self.assertEquals('View Notifications' in channels_template, True)
    self.assertEquals('Channel ID: ' in channels_template, True)
    self.assertEquals('Resource ID: ' in channels_template, True)
    self.assertEquals(FAKE_EVENT in channels_template, True)
    self.assertEquals(FAKE_CHANNEL_ID in channels_template, True)
    self.assertEquals(FAKE_RESOURCE_ID in channels_template, True)
