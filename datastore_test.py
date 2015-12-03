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
FAKE_CLIENT_SECRET = 'secret abc'
BAD_CLIENT_ID = 'id5678'
BAD_CLIENT_SECRET = 'secret 123'

# Domain Verification test globals
FAKE_CONTENT = 'foo'
BAD_CONTENT = 'bar'


class DatastoreTest(unittest.TestCase):

  def setUp(self):
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
    global FAKE_KEY, FAKE_KEY_URLSAFE, FAKE_USER
    FAKE_KEY = ndb.Key(datastore.User, FAKE_EMAIL)
    FAKE_KEY_URLSAFE = FAKE_KEY.urlsafe()
    FAKE_USER = datastore.User(key=FAKE_KEY, email=FAKE_EMAIL,
                               name=FAKE_NAME,
                               public_key=FAKE_PUBLIC_KEY,
                               private_key=FAKE_PRIVATE_KEY)
    global BAD_KEY, BAD_KEY_URLSAFE, USER_BAD_KEY
    BAD_KEY = ndb.Key(datastore.User, BAD_EMAIL)
    BAD_KEY_URLSAFE = BAD_KEY.urlsafe()
    USER_BAD_KEY = datastore.User(key=BAD_KEY, email=BAD_EMAIL,
                                  name=FAKE_NAME,
                                  public_key=BAD_PUB_PRI_KEY,
                                  private_key=BAD_PUB_PRI_KEY)

  def tearDown(self):
    self.testbed.deactivate()

  def testGetCount(self):
    self.assertEqual(datastore.User.GetCount(), 0)

    FAKE_USER.put()
    self.assertEqual(datastore.User.GetCount(), 1)

    USER_BAD_KEY.put()
    self.assertEqual(datastore.User.GetCount(), 2)

  def testGetAll(self):
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
    self.assertEqual(datastore.User.Get(FAKE_KEY.id()), None)
    self.assertEqual(datastore.User.Get(BAD_KEY.id()), None)

    FAKE_USER.put()
    self.assertEqual(datastore.User.Get(FAKE_KEY.id()), FAKE_USER)
    self.assertEqual(datastore.User.Get(BAD_KEY.id()), None)

    USER_BAD_KEY.put()
    self.assertEqual(datastore.User.Get(FAKE_KEY.id()), FAKE_USER)
    self.assertEqual(datastore.User.Get(BAD_KEY.id()), USER_BAD_KEY)

  def testGetByKey(self):
    self.assertEqual(datastore.User.GetByKey(FAKE_KEY_URLSAFE), None)
    self.assertEqual(datastore.User.GetByKey(BAD_KEY_URLSAFE), None)

    FAKE_USER.put()
    self.assertEqual(datastore.User.GetByKey(FAKE_KEY_URLSAFE), FAKE_USER)
    self.assertEqual(datastore.User.GetByKey(BAD_KEY_URLSAFE), None)

    USER_BAD_KEY.put()
    self.assertEqual(datastore.User.GetByKey(FAKE_KEY_URLSAFE), FAKE_USER)
    self.assertEqual(datastore.User.GetByKey(BAD_KEY_URLSAFE), USER_BAD_KEY)

  def testDelete(self):
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

  @patch.object(ndb, 'Key')
  @patch('hashlib.sha256.hexdigest')
  @patch.object(datastore.hashlib, 'sha256')
  def testCreateUser(self, mock_sha, mock_hex, mock_key):
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

  @patch('base64.urlsafe_b64encode')
  @patch.object(datastore.RSA._RSAobj, 'publickey')
  @patch('datastore.RSA._RSAobj.exportKey')
  @patch.object(datastore.RSA, 'generate')
  def testGenerateKeyPair(self, mock_rsa, mock_exp, mock_pub, mock_encode):
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
    USER_BAD_KEY.put()
    user_before_test = datastore.User.GetByKey(BAD_KEY_URLSAFE)
    self.assertEqual(user_before_test.public_key, BAD_PUB_PRI_KEY)
    self.assertEqual(user_before_test.private_key, BAD_PUB_PRI_KEY)

    mock_generate.return_value = FAKE_KEY_PAIR

    datastore.User._UpdateKeyPair(BAD_KEY_URLSAFE)

    mock_generate.assert_called_once_with()
    user_after_test = datastore.User.GetByKey(BAD_KEY_URLSAFE)
    self.assertEqual(user_after_test.public_key, FAKE_PUBLIC_KEY)
    self.assertEqual(user_after_test.private_key, FAKE_PRIVATE_KEY)

  @patch('datastore.User._CreateUser')
  def testInsertUser(self, mock_create):
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
    # Mock create function to return FAKE_USER and USER_BAD_KEY
    def side_effect(arg1, arg2):
        if arg1 is FAKE_DIRECTORY_USER:
            return FAKE_USER
        else:
            return USER_BAD_KEY
    mock_create.side_effect = side_effect
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

  def testInsert(self):
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


class OAuthDatastoreTest(DatastoreTest):

  def testGetOrInsertDefault(self):
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
    self.assertEqual(datastore.OAuth.GetCount(), 0)

    datastore.OAuth.InsertDefault()

    self.assertEqual(datastore.OAuth.GetCount(), 1)
    oauth_after_insert = datastore.OAuth.GetAll()
    for client in oauth_after_insert:
        self.assertEqual(client.key.id(), datastore.OAuth.CLIENT_SECRET_ID)
        self.assertEqual(client.client_id, datastore.OAuth.DEFAULT_ID)
        self.assertEqual(client.client_secret, datastore.OAuth.DEFAULT_SECRET)

  def testInsert(self):
    self.assertEqual(datastore.OAuth.GetCount(), 0)

    datastore.OAuth.Insert(FAKE_CLIENT_ID, FAKE_CLIENT_SECRET)

    self.assertEqual(datastore.OAuth.GetCount(), 1)
    oauth_after_insert = datastore.OAuth.GetAll()
    for client in oauth_after_insert:
        self.assertEqual(client.key.id(), datastore.OAuth.CLIENT_SECRET_ID)
        self.assertEqual(client.client_id, FAKE_CLIENT_ID)
        self.assertEqual(client.client_secret, FAKE_CLIENT_SECRET)

  def testUpdate(self):
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
    datastore.OAuth.Flush()

    mock_flush_all.assert_called_once_with()

class DomainVerificationDatastoreTest(DatastoreTest):

  def testGetOrInsertDefault(self):
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
    self.assertEqual(DomainVerification.GetCount(), 0)

    DomainVerification.InsertDefault()

    self.assertEqual(DomainVerification.GetCount(), 1)
    dv_after_insert = DomainVerification.Get(DomainVerification.CONTENT_ID)
    self.assertEqual(dv_after_insert.key.id(),
                     DomainVerification.CONTENT_ID)
    self.assertEqual(dv_after_insert.content,
                     DomainVerification.DEFAULT_CONTENT)

  def testInsert(self):
    self.assertEqual(DomainVerification.GetCount(), 0)

    DomainVerification.Insert(FAKE_CONTENT)

    self.assertEqual(DomainVerification.GetCount(), 1)
    dv_after_insert = DomainVerification.Get(DomainVerification.CONTENT_ID)
    self.assertEqual(dv_after_insert.key.id(),
                     DomainVerification.CONTENT_ID)
    self.assertEqual(dv_after_insert.content, FAKE_CONTENT)

  def testUpdate(self):
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
