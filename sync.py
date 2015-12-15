"""The user sync module for handling user changes in the directory service."""

import admin
from appengine_config import JINJA_ENVIRONMENT
from config import PATHS
from datastore import Notification
from datastore import NotificationChannel
from error_handlers import Handle500
from googleapiclient import errors
from google_directory_service import GoogleDirectoryService
import json
import webapp2



def _RenderNotificationsTemplate():
  """Render a list of notifications."""
  notifications = Notification.GetAll()
  template_values = {
      'notifications': notifications
  }
  template = JINJA_ENVIRONMENT.get_template('templates/notifications.html')
  return template.render(template_values)

def _RenderChannelsListTemplate():
  """Render a list of notification channels."""
  channels = NotificationChannel.GetAll()
  template_values = {
      'channels': channels
  }
  html_file_name = 'templates/notification_channels.html'
  template = JINJA_ENVIRONMENT.get_template(html_file_name)
  return template.render(template_values)


class PushNotificationHandler(webapp2.RequestHandler):

  """Receive an update about users in the datastore."""

  # pylint: disable=too-few-public-methods

  def post(self):
    """Receive push notifications and issue some sort of response."""
    state = self.request.headers.get('X-Goog-Resource-State')
    number = self.request.headers.get('X-Goog-Message-Number')
    json_body = self.request.body
    body_object = json.loads(json_body)
    uuid = body_object['id']
    email = body_object['primaryEmail']
    Notification.Insert(state=state, number=number, uuid=uuid, email=email)
    self.response.write('Got a notification!')


class DefaultPathHandler(webapp2.RequestHandler):

  """Base page for all pages under /sync."""

  # pylint: disable=too-few-public-methods

  @admin.OAUTH_DECORATOR.oauth_required
  @admin.RequireAppOrDomainAdmin
  def get(self):
    """Redirect to the list of previous notifications."""
    self.redirect(PATHS['notifications_list'])


class ListChannelsHandler(webapp2.RequestHandler):

  """List all the channels currently receiving notifications."""

  # pylint: disable=too-few-public-methods

  @admin.OAUTH_DECORATOR.oauth_required
  @admin.RequireAppOrDomainAdmin
  def get(self):
    """List all the channels and associated properties in the datastore."""
    self.response.write(_RenderChannelsListTemplate())


class ListNotificationsHandler(webapp2.RequestHandler):

  """List all the notifications previously received."""

  # pylint: disable=too-few-public-methods

  @admin.OAUTH_DECORATOR.oauth_required
  @admin.RequireAppOrDomainAdmin
  def get(self):
    """List all previous notifications received."""
    self.response.write(_RenderNotificationsTemplate())


class WatchUserDeleteEventHandler(webapp2.RequestHandler):

  """Watch users in the directory API for deletion events."""

  # pylint: disable=too-few-public-methods

  @admin.OAUTH_DECORATOR.oauth_required
  @admin.RequireAppOrDomainAdmin
  def get(self):
    """Perform a pub/sub for user delete events."""
    try:
      directory_service = GoogleDirectoryService(admin.OAUTH_DECORATOR)
      directory_service.WatchUsers('delete')
      self.redirect(PATHS['notification_channels_list'])
    except errors.HttpError as error:
      self.response.write('An error occurred: ' + str(error))


class UnsubscribeHandler(webapp2.RequestHandler):

  """Unsubsribe from notifications for a specific resouce."""

  # pylint: disable=too-few-public-methods

  @admin.OAUTH_DECORATOR.oauth_required
  @admin.RequireAppOrDomainAdmin
  def get(self):
    """Find the channel specified and unsubscribe from it."""
    datastore_id = int(self.request.get('id'))
    entity = NotificationChannel.Get(datastore_id)
    try:
      directory_service = GoogleDirectoryService(admin.OAUTH_DECORATOR)
      directory_service.StopNotifications(entity)
      self.redirect(PATHS['notification_channels_list'])
    except errors.HttpError as error:
      self.response.write('An error occurred: ' + str(error))


APP = webapp2.WSGIApplication([
    (PATHS['receive_push_notifications'], PushNotificationHandler),
    (PATHS['sync_top_level_path'], DefaultPathHandler),
    (PATHS['notification_channels_list'], ListChannelsHandler),
    (PATHS['notifications_list'], ListNotificationsHandler),
    (PATHS['watch_for_user_deletion'], WatchUserDeleteEventHandler),
    (PATHS['unsubscribe_from_notifications'], UnsubscribeHandler),
    (admin.OAUTH_DECORATOR.callback_path,
     admin.OAUTH_DECORATOR.callback_handler()),
], debug=True)

# This is the only way to catch exceptions from the oauth decorators.
APP.error_handlers[500] = Handle500
