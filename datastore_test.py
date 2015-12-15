"""Test datastore module functionality."""
import unittest

from mock import patch

import datastore

from google.appengine.ext import ndb
from google.appengine.ext import testbed
from datastore import DomainVerification

# User test globals
FAKE_EMAIL = 'foo@bar.com'
FAKE_NAME = 'Mr. Foo Bar Jr.'
FAKE_PUBLIC_KEY = 'fakePublicKey'
FAKE_PRIVATE_KEY = 'fakePrivateKey'
FAKE_DIRECTORY_USER = {}
FAKE_DIRECTORY_USER['primaryEmail'] = FAKE_EMAIL
FAKE_DIRECTORY_USER['name'] = {}
FAKE_DIRECTORY_USER['name']['fullName'] = FAKE_NAME
FAKE_KEY_PAIR = {}
FAKE_KEY_PAIR['private_key'] = FAKE_PRIVATE_KEY
FAKE_KEY_PAIR['public_key'] = FAKE_PUBLIC_KEY
BAD_EMAIL = 'bazbar@foo.com'
BAD_PUB_PRI_KEY = 'foo'
BAD_DIR_USER = {}
BAD_DIR_USER['primaryEmail'] = BAD_EMAIL
BAD_DIR_USER['name'] = {}
BAD_DIR_USER['name']['fullName'] = FAKE_NAME

# Proxy server test globals
FAKE_PROXY_SERVER_NAME = 'US_WEST1'
FAKE_IP = '000.000.000.000'
FAKE_SSH_PRI_KEY = 'fake private key'
FAKE_FINGERPRINT = 'fake thumb'
BAD_PROXY_SERVER_NAME = 'bad proxy server'
BAD_IP = '111.111.111.111'
BAD_SSH_PRI_KEY = 'this is a bad private key'
BAD_FINGERPRINT = 'pinky'

# OAuth test globals
FAKE_CLIENT_ID = 'id1234'
BAD_CLIENT_ID = 'id5678'
# The comment below disables landscape.io checking on that line so that it
# does not think we have an actual secret stored which we do not. The
# object it is used to get has a parameter which is the actual secret. This
# however is not.
FAKE_CLIENT_SECRET = 'secret abc'  # noqa
BAD_CLIENT_SECRET = 'secret 123'  # noqa

# Domain Verification test globals
FAKE_CONTENT = 'foo'
BAD_CONTENT = 'bar'

# Notification test globals
FAKE_STATE = 'delete'
FAKE_NUMBER = '1000000'
FAKE_UUID = '123087632460958036'

# Notification Channels test globals
FAKE_EVENT = 'delete'
FAKE_CHANNEL_ID = 'foo customer_delete_time-in-millis'
FAKE_RESOURCE_ID = 'i am a fake resource id'


class DatastoreTest(unittest.TestCase):

  """Test basic datastore class functionality."""

  def setUp(self):
    """Setup the testbed for each test class."""
    # First, create an instance of the Testbed class.
    self.testbed = testbed.Testbed()
    # Then activate the testbed, which prepares the service stubs for use.
    self.testbed.activate()
    # Next, declare which service stubs you want to use.
    self.testbed.init_datastore_v3_stub()
    self.testbed.init_memcache_stub()
    # Clear ndb's in-context cache between tests.
    # This prevents data from leaking between tests.
    # Alternatively, you could disable caching by
    # using ndb.get_context().set_cache_policy(False)
    ndb.get_context().clear_cache()

    self.assertTrue(BAD_PUB_PRI_KEY is not FAKE_PUBLIC_KEY)
    self.assertTrue(BAD_PUB_PRI_KEY is not FAKE_PRIVATE_KEY)
    # I have to define the keys here once the module is loaded and
    # stubbed so that the call to ndb.Key is the stubbed version.
    global FAKE_KEY, FAKE_KEY_URLSAFE, FAKE_USER  # noqa
    FAKE_KEY = ndb.Key(datastore.User, FAKE_EMAIL)
    FAKE_KEY_URLSAFE = FAKE_KEY.urlsafe()
    FAKE_USER = datastore.User(key=FAKE_KEY, email=FAKE_EMAIL,
                               name=FAKE_NAME,
                               public_key=FAKE_PUBLIC_KEY,
                               private_key=FAKE_PRIVATE_KEY,
                               is_key_revoked=False)
    global BAD_KEY, BAD_KEY_URLSAFE, USER_BAD_KEY  # noqa
    BAD_KEY = ndb.Key(datastore.User, BAD_EMAIL)
    BAD_KEY_URLSAFE = BAD_KEY.urlsafe()
    USER_BAD_KEY = datastore.User(key=BAD_KEY, email=BAD_EMAIL,
                                  name=FAKE_NAME,
                                  public_key=BAD_PUB_PRI_KEY,
                                  private_key=BAD_PUB_PRI_KEY,
                                  is_key_revoked=False)

  def tearDown(self):
    """Deactive the testbed."""
    self.testbed.deactivate()

  def testGetCount(self):
    """Test that the count of entities of a given type is returned."""
    self.assertEqual(datastore.User.GetCount(), 0)

    FAKE_USER.put()
    self.assertEqual(datastore.User.GetCount(), 1)

    USER_BAD_KEY.put()
    self.assertEqual(datastore.User.GetCount(), 2)

  def testGetAll(self):
    """Test that all entities of a given type are found and returned."""
    self.assertEqual(datastore.User.GetAll(), [])
    self.assertEqual(len(datastore.User.GetAll()), datastore.User.GetCount())

    FAKE_USER.put()
    self.assertTrue(FAKE_USER in datastore.User.GetAll())
    self.assertTrue(USER_BAD_KEY not in datastore.User.GetAll())
    self.assertEqual(len(datastore.User.GetAll()), datastore.User.GetCount())

    USER_BAD_KEY.put()
    self.assertTrue(FAKE_USER in datastore.User.GetAll())
    self.assertTrue(USER_BAD_KEY in datastore.User.GetAll())
    self.assertEqual(len(datastore.User.GetAll()), datastore.User.GetCount())

  def testGet(self):
    """Test that an entity is found by id and returned from the datastore."""
    self.assertEqual(datastore.User.Get(FAKE_KEY.id()), None)
    self.assertEqual(datastore.User.Get(BAD_KEY.id()), None)

    FAKE_USER.put()
    self.assertEqual(datastore.User.Get(FAKE_KEY.id()), FAKE_USER)
    self.assertEqual(datastore.User.Get(BAD_KEY.id()), None)

    USER_BAD_KEY.put()
    self.assertEqual(datastore.User.Get(FAKE_KEY.id()), FAKE_USER)
    self.assertEqual(datastore.User.Get(BAD_KEY.id()), USER_BAD_KEY)

  def testGetByKey(self):
    """Test that an entity is found by key and returned from the datastore."""
    self.assertEqual(datastore.User.GetByKey(FAKE_KEY_URLSAFE), None)
    self.assertEqual(datastore.User.GetByKey(BAD_KEY_URLSAFE), None)

    FAKE_USER.put()
    self.assertEqual(datastore.User.GetByKey(FAKE_KEY_URLSAFE), FAKE_USER)
    self.assertEqual(datastore.User.GetByKey(BAD_KEY_URLSAFE), None)

    USER_BAD_KEY.put()
    self.assertEqual(datastore.User.GetByKey(FAKE_KEY_URLSAFE), FAKE_USER)
    self.assertEqual(datastore.User.GetByKey(BAD_KEY_URLSAFE), USER_BAD_KEY)

  def testDelete(self):
    """Test that an entity is found by id and removed from the datastore."""
    FAKE_USER.put()
    USER_BAD_KEY.put()
    self.assertTrue(FAKE_USER in datastore.User.GetAll())
    self.assertTrue(USER_BAD_KEY in datastore.User.GetAll())

    datastore.User.Delete(FAKE_KEY.id())

    self.assertTrue(FAKE_USER not in datastore.User.GetAll())
    self.assertTrue(USER_BAD_KEY in datastore.User.GetAll())

    datastore.User.Delete(BAD_KEY.id())

    self.assertTrue(FAKE_USER not in datastore.User.GetAll())
    self.assertTrue(USER_BAD_KEY not in datastore.User.GetAll())

  def testDeleteByKey(self):
    """Test that an entity is found by key and removed from the datastore."""
    FAKE_USER.put()
    USER_BAD_KEY.put()
    self.assertTrue(FAKE_USER in datastore.User.GetAll())
    self.assertTrue(USER_BAD_KEY in datastore.User.GetAll())

    datastore.User.DeleteByKey(FAKE_KEY_URLSAFE)

    self.assertTrue(FAKE_USER not in datastore.User.GetAll())
    self.assertTrue(USER_BAD_KEY in datastore.User.GetAll())

    datastore.User.DeleteByKey(BAD_KEY_URLSAFE)

    self.assertTrue(FAKE_USER not in datastore.User.GetAll())
    self.assertTrue(USER_BAD_KEY not in datastore.User.GetAll())


class UserDatastoreTest(DatastoreTest):

  """Test user datastore class functionality."""

  @patch.object(ndb, 'Key')
  @patch('hashlib.sha256.hexdigest')
  @patch.object(datastore.hashlib, 'sha256')
  def testCreateUser(self, mock_sha, mock_hex, mock_key):
    """Test that a new user entity is created with the associated fields."""
    fake_hex_email = '0x12345678'
    mock_hex.return_value = fake_hex_email
    mock_sha.return_value.hexdigest = mock_hex
    mock_key.return_value = FAKE_KEY

    user_entity = datastore.User._CreateUser(FAKE_DIRECTORY_USER, FAKE_KEY_PAIR)

    mock_sha.assert_called_once_with(FAKE_EMAIL)
    mock_hex.assert_called_once_with()
    mock_key.assert_called_once_with(datastore.User, fake_hex_email)
    self.assertEqual(user_entity.key, FAKE_KEY)
    self.assertEqual(user_entity.email, FAKE_EMAIL)
    self.assertEqual(user_entity.name, FAKE_NAME)
    self.assertEqual(user_entity.public_key, FAKE_PUBLIC_KEY)
    self.assertEqual(user_entity.private_key, FAKE_PRIVATE_KEY)
    self.assertEqual(user_entity.is_key_revoked, False)

  @patch('base64.urlsafe_b64encode')
  @patch.object(datastore.RSA._RSAobj, 'publickey')
  @patch('datastore.RSA._RSAobj.exportKey')
  @patch.object(datastore.RSA, 'generate')
  def testGenerateKeyPair(self, mock_rsa, mock_exp, mock_pub, mock_encode):
    """Test that a new key pair is created successfully."""
    mock_encode.return_value = FAKE_PRIVATE_KEY
    mock_exp.return_value = FAKE_PRIVATE_KEY
    mock_pub.return_value.exportKey = mock_exp
    mock_rsa.return_value.exportKey = mock_exp
    mock_rsa.return_value.publickey = mock_pub

    pair = datastore.User._GenerateKeyPair()

    mock_rsa.assert_called_once_with(2048)
    self.assertEqual(mock_exp.call_count, 2)
    mock_pub.assert_called_once_with()
    self.assertEqual(mock_encode.call_count, 2)
    mock_encode.assert_any_call(FAKE_PRIVATE_KEY)
    self.assertEqual(pair['public_key'], FAKE_PRIVATE_KEY)
    self.assertEqual(pair['private_key'], FAKE_PRIVATE_KEY)

  @patch('datastore.User._GenerateKeyPair')
  def testUpdateKeyPair(self, mock_generate):
    """Test the key pair is updated for a given user."""
    USER_BAD_KEY.put()
    user_before_test = datastore.User.GetByKey(BAD_KEY_URLSAFE)
    self.assertEqual(user_before_test.public_key, BAD_PUB_PRI_KEY)
    self.assertEqual(user_before_test.private_key, BAD_PUB_PRI_KEY)

    mock_generate.return_value = FAKE_KEY_PAIR

    datastore.User.UpdateKeyPair(BAD_KEY_URLSAFE)

    mock_generate.assert_called_once_with()
    user_after_test = datastore.User.GetByKey(BAD_KEY_URLSAFE)
    self.assertEqual(user_after_test.public_key, FAKE_PUBLIC_KEY)
    self.assertEqual(user_after_test.private_key, FAKE_PRIVATE_KEY)

  def testToggleKeyRevoked(self):
    """Test the is_key_revoked property is flipped on each call."""
    FAKE_USER.put()
    user_before_test = datastore.User.GetByKey(FAKE_KEY_URLSAFE)
    self.assertEqual(user_before_test.is_key_revoked, False)

    datastore.User.ToggleKeyRevoked(FAKE_KEY_URLSAFE)

    user_after_first_toggle = datastore.User.GetByKey(FAKE_KEY_URLSAFE)
    self.assertEqual(user_after_first_toggle.is_key_revoked, True)

    datastore.User.ToggleKeyRevoked(FAKE_KEY_URLSAFE)

    user_after_second_toggle = datastore.User.GetByKey(FAKE_KEY_URLSAFE)
    self.assertEqual(user_after_second_toggle.is_key_revoked, False)

  @patch('datastore.User._CreateUser')
  def testInsertUser(self, mock_create):
    """Test that a new user is inserted and found after."""
    mock_create.return_value = FAKE_USER

    user_before_test = datastore.User.GetByKey(FAKE_KEY_URLSAFE)
    self.assertEqual(user_before_test, None)

    datastore.User.InsertUser(FAKE_DIRECTORY_USER, FAKE_KEY_PAIR)

    mock_create.assert_called_once_with(FAKE_DIRECTORY_USER, FAKE_KEY_PAIR)

    user_after_test = datastore.User.GetByKey(FAKE_KEY_URLSAFE)
    self.assertEqual(user_after_test, FAKE_USER)

  @patch('datastore.User._GenerateKeyPair')
  @patch('datastore.User._CreateUser')
  def testInsertUsers(self, mock_create, mock_generate):
    """Test the insert users function."""
    def SideEffect(arg1, arg2):
      """Mock create function to return FAKE_USER and USER_BAD_KEY."""
      # pylint: disable=unused-argument
      if arg1 is FAKE_DIRECTORY_USER:
        return FAKE_USER
      else:
        return USER_BAD_KEY
    mock_create.side_effect = SideEffect
    mock_generate.return_value = FAKE_KEY_PAIR
    # Create a list of directory users
    directory_users = []
    directory_users.append(BAD_DIR_USER)
    directory_users.append(FAKE_DIRECTORY_USER)
    # Check that datastore is empty
    self.assertEqual(datastore.User.GetCount(), 0)
    users_before_test = datastore.User.GetAll()
    self.assertTrue(not users_before_test)

    datastore.User.InsertUsers(directory_users)

    self.assertEqual(mock_generate.call_count, len(directory_users))
    mock_create.assert_any_call(FAKE_DIRECTORY_USER, FAKE_KEY_PAIR)
    mock_create.assert_any_call(BAD_DIR_USER, FAKE_KEY_PAIR)

    self.assertEqual(datastore.User.GetCount(), len(directory_users))
    users_after_test = datastore.User.GetAll()
    self.assertTrue(USER_BAD_KEY in users_after_test)
    self.assertTrue(FAKE_USER in users_after_test)


class ProxyServerDatastoreTest(DatastoreTest):

  """Test proxy server datastore class functionality."""

  def testInsert(self):
    """Test that a new proxy server is properly inserted and found after."""
    self.assertEqual(datastore.ProxyServer.GetCount(), 0)

    datastore.ProxyServer.Insert(FAKE_PROXY_SERVER_NAME, FAKE_IP,
                                 FAKE_SSH_PRI_KEY, FAKE_FINGERPRINT)

    self.assertEqual(datastore.ProxyServer.GetCount(), 1)
    proxys_after_insert = datastore.ProxyServer.GetAll()
    for proxy in proxys_after_insert:
      self.assertEqual(proxy.name, FAKE_PROXY_SERVER_NAME)
      self.assertEqual(proxy.ip_address, FAKE_IP)
      self.assertEqual(proxy.ssh_private_key, FAKE_SSH_PRI_KEY)
      self.assertEqual(proxy.fingerprint, FAKE_FINGERPRINT)

  def testUpdate(self):
    """Test that an existing proxy server is properly updated."""
    bad_proxy = datastore.ProxyServer(name=BAD_PROXY_SERVER_NAME,
                                      ip_address=BAD_IP,
                                      ssh_private_key=BAD_SSH_PRI_KEY,
                                      fingerprint=BAD_FINGERPRINT)
    bad_proxy.put()
    bad_proxy_id = datastore.ProxyServer.GetAll()[0].key.id()

    self.assertEqual(datastore.ProxyServer.GetCount(), 1)
    proxy_before_update = datastore.ProxyServer.Get(bad_proxy_id)
    self.assertEqual(proxy_before_update.name, BAD_PROXY_SERVER_NAME)
    self.assertEqual(proxy_before_update.ip_address, BAD_IP)
    self.assertEqual(proxy_before_update.ssh_private_key, BAD_SSH_PRI_KEY)
    self.assertEqual(proxy_before_update.fingerprint, BAD_FINGERPRINT)

    datastore.ProxyServer.Update(bad_proxy_id, FAKE_PROXY_SERVER_NAME, FAKE_IP,
                                 FAKE_SSH_PRI_KEY, FAKE_FINGERPRINT)

    self.assertEqual(datastore.ProxyServer.GetCount(), 1)
    proxy_after_update = datastore.ProxyServer.Get(bad_proxy_id)
    self.assertEqual(proxy_after_update.name, FAKE_PROXY_SERVER_NAME)
    self.assertEqual(proxy_after_update.ip_address, FAKE_IP)
    self.assertEqual(proxy_after_update.ssh_private_key, FAKE_SSH_PRI_KEY)
    self.assertEqual(proxy_after_update.fingerprint, FAKE_FINGERPRINT)


class NotificationDatastoreTest(DatastoreTest):

  """Test notification datastore class functionality."""

  def testInsert(self):
    """Test that a new notification is properly inserted and found after."""
    self.assertEqual(datastore.Notification.GetCount(), 0)

    datastore.Notification.Insert(FAKE_STATE, FAKE_NUMBER, FAKE_UUID,
                                  FAKE_EMAIL)

    self.assertEqual(datastore.Notification.GetCount(), 1)
    notifications_after_insert = datastore.Notification.GetAll()
    for notification in notifications_after_insert:
      self.assertEqual(notification.state, FAKE_STATE)
      self.assertEqual(notification.number, FAKE_NUMBER)
      self.assertEqual(notification.uuid, FAKE_UUID)
      self.assertEqual(notification.email, FAKE_EMAIL)


class NotificationChannelDSTest(DatastoreTest):

  """Test notification channels datastore class functionality."""

  def testInsert(self):
    """Test that a new notification channel is properly inserted and found."""
    self.assertEqual(datastore.NotificationChannel.GetCount(), 0)

    datastore.NotificationChannel.Insert(FAKE_EVENT, FAKE_CHANNEL_ID,
                                         FAKE_RESOURCE_ID)

    self.assertEqual(datastore.NotificationChannel.GetCount(), 1)
    channels_after_insert = datastore.NotificationChannel.GetAll()
    for channel in channels_after_insert:
      self.assertEqual(channel.event, FAKE_EVENT)
      self.assertEqual(channel.channel_id, FAKE_CHANNEL_ID)
      self.assertEqual(channel.resource_id, FAKE_RESOURCE_ID)


class OAuthDatastoreTest(DatastoreTest):

  """Test oauth datastore class functionality."""

  def testGetOrInsertDefault(self):
    """Test that an entity is always returned and insert if necessary."""
    self.assertEqual(datastore.OAuth.GetCount(), 0)

    first_entity = datastore.OAuth.GetOrInsertDefault()

    self.assertEqual(datastore.OAuth.GetCount(), 1)
    self.assertEqual(first_entity.key.id(), datastore.OAuth.CLIENT_SECRET_ID)
    self.assertEqual(first_entity.client_id, datastore.OAuth.DEFAULT_ID)
    self.assertEqual(first_entity.client_secret, datastore.OAuth.DEFAULT_SECRET)

    datastore.OAuth.Update(FAKE_CLIENT_ID, FAKE_CLIENT_SECRET)

    second_entity = datastore.OAuth.GetOrInsertDefault()

    self.assertEqual(datastore.OAuth.GetCount(), 1)
    self.assertEqual(second_entity.key.id(), datastore.OAuth.CLIENT_SECRET_ID)
    self.assertEqual(second_entity.client_id, FAKE_CLIENT_ID)
    self.assertEqual(second_entity.client_secret, FAKE_CLIENT_SECRET)

  def testInsertDefault(self):
    """Test that a default entity is inserted and found afterwards."""
    self.assertEqual(datastore.OAuth.GetCount(), 0)

    datastore.OAuth.InsertDefault()

    self.assertEqual(datastore.OAuth.GetCount(), 1)
    oauth_after_insert = datastore.OAuth.GetAll()
    for client in oauth_after_insert:
      self.assertEqual(client.key.id(), datastore.OAuth.CLIENT_SECRET_ID)
      self.assertEqual(client.client_id, datastore.OAuth.DEFAULT_ID)
      self.assertEqual(client.client_secret, datastore.OAuth.DEFAULT_SECRET)

  def testInsert(self):
    """Test that an entity is inserted and found afterwards."""
    self.assertEqual(datastore.OAuth.GetCount(), 0)

    datastore.OAuth.Insert(FAKE_CLIENT_ID, FAKE_CLIENT_SECRET)

    self.assertEqual(datastore.OAuth.GetCount(), 1)
    oauth_after_insert = datastore.OAuth.GetAll()
    for client in oauth_after_insert:
      self.assertEqual(client.key.id(), datastore.OAuth.CLIENT_SECRET_ID)
      self.assertEqual(client.client_id, FAKE_CLIENT_ID)
      self.assertEqual(client.client_secret, FAKE_CLIENT_SECRET)

  def testUpdate(self):
    """Test that an existing entity is updated with new values."""
    datastore.OAuth.Insert(BAD_CLIENT_ID, BAD_CLIENT_SECRET)

    self.assertEqual(datastore.OAuth.GetCount(), 1)
    oauth_before_update = datastore.OAuth.Get(datastore.OAuth.CLIENT_SECRET_ID)
    self.assertEqual(oauth_before_update.client_id, BAD_CLIENT_ID)
    self.assertEqual(oauth_before_update.client_secret, BAD_CLIENT_SECRET)

    datastore.OAuth.Update(FAKE_CLIENT_ID, FAKE_CLIENT_SECRET)

    self.assertEqual(datastore.OAuth.GetCount(), 1)
    oauth_after_update = datastore.OAuth.Get(datastore.OAuth.CLIENT_SECRET_ID)
    self.assertEqual(oauth_after_update.client_id, FAKE_CLIENT_ID)
    self.assertEqual(oauth_after_update.client_secret, FAKE_CLIENT_SECRET)

  @patch('datastore.memcache.flush_all')
  def testFlush(self, mock_flush_all):
    """Test that oauth is flushed from the memcache."""
    # pylint: disable=no-self-use
    datastore.OAuth.Flush()

    mock_flush_all.assert_called_once_with()

class DomainVerificationDatastoreTest(DatastoreTest):

  """Test domain verification datastore class functionality."""

  def testGetOrInsertDefault(self):
    """Test that an entity is always returned and insert if necessary."""
    self.assertEqual(DomainVerification.GetCount(), 0)

    first_entity = DomainVerification.GetOrInsertDefault()

    self.assertEqual(DomainVerification.GetCount(), 1)
    self.assertEqual(first_entity.key.id(),
                     DomainVerification.CONTENT_ID)
    self.assertEqual(first_entity.content,
                     DomainVerification.DEFAULT_CONTENT)

    DomainVerification.Update(FAKE_CONTENT)

    second_entity = DomainVerification.GetOrInsertDefault()

    self.assertEqual(DomainVerification.GetCount(), 1)
    self.assertEqual(second_entity.key.id(),
                     DomainVerification.CONTENT_ID)
    self.assertEqual(second_entity.content, FAKE_CONTENT)

  def testInsertDefault(self):
    """Test that a default entity is inserted and found afterwards."""
    self.assertEqual(DomainVerification.GetCount(), 0)

    DomainVerification.InsertDefault()

    self.assertEqual(DomainVerification.GetCount(), 1)
    dv_after_insert = DomainVerification.Get(DomainVerification.CONTENT_ID)
    self.assertEqual(dv_after_insert.key.id(),
                     DomainVerification.CONTENT_ID)
    self.assertEqual(dv_after_insert.content,
                     DomainVerification.DEFAULT_CONTENT)

  def testInsert(self):
    """Test that an entity is inserted and found afterwards."""
    self.assertEqual(DomainVerification.GetCount(), 0)

    DomainVerification.Insert(FAKE_CONTENT)

    self.assertEqual(DomainVerification.GetCount(), 1)
    dv_after_insert = DomainVerification.Get(DomainVerification.CONTENT_ID)
    self.assertEqual(dv_after_insert.key.id(),
                     DomainVerification.CONTENT_ID)
    self.assertEqual(dv_after_insert.content, FAKE_CONTENT)

  def testUpdate(self):
    """Test that an existing entity is updated with new values."""
    DomainVerification.Insert(BAD_CONTENT)

    self.assertEqual(DomainVerification.GetCount(), 1)
    dv_before_update = DomainVerification.Get(DomainVerification.CONTENT_ID)
    self.assertEqual(dv_before_update.content, BAD_CONTENT)

    DomainVerification.Update(FAKE_CONTENT)

    self.assertEqual(DomainVerification.GetCount(), 1)
    dv_after_update = DomainVerification.Get(DomainVerification.CONTENT_ID)
    self.assertEqual(dv_after_update.content, FAKE_CONTENT)

if __name__ == '__main__':
  unittest.main()
