"""Module to interact with datastore models and helper functions.

TODO(henry): Refactor the common methods (get, insert, delete) into base class.
"""

import base64
import binascii
from Crypto.PublicKey import RSA
from google.appengine.api import memcache
from google.appengine.ext import ndb
import hashlib
import json
import os


class BaseModel(ndb.Model):
  
  @classmethod
  def GetCount(cls):
    """Get a count of all the entities in the datastore.

    Args:
      cls is an object that holds the sub-class itself, not an instance
      of the sub-class.

    Returns:
      An integer of all the entities in the datastore.
    """
    q = cls.query()
    return q.count()

  @classmethod
  def GetAll(cls):
    """Get all entities from datastore.

    Args:
      cls is an object that holds the sub-class itself, not an instance
      of the sub-class.

    Returns:
      A list of datastore entities.
    """
    q = cls.query()
    return q.fetch()
  
  @classmethod
  def Get(cls, id):
    """Get a single entity by id from datastore.

    Args:
      cls is an object that holds the sub-class itself, not an instance
      of the sub-class.
      id: A integer or a string of the entity's id.  Auto assigned id will be
          integers.

    Returns:
      A datastore entity.
    """
    return cls.get_by_id(id)
  
  @classmethod
  def GetByKey(cls, url_key):
    """Get a single entity by id from datastore.

    Args:
      cls is an object that holds the sub-class itself, not an instance
      of the sub-class.
      url_key: The url encoded key for an entity in the datastore.

    Returns:
      A datastore entity.
    """
    key = ndb.Key(urlsafe=url_key)
    return key.get()

  @classmethod
  def Delete(cls, id):
    """Delete an entity from the datastore.

    Args:
      cls is an object that holds the sub-class itself, not an instance
      of the sub-class.
      id: A integer or a string of the entity's id.  Auto assigned id will be
          integers.
    """
    key = ndb.Key(cls, id)
    key.delete()

  @classmethod
  def DeleteByKey(cls, url_key):
    """Delete an entity from the datastore.

    Args:
      cls is an object that holds the sub-class itself, not an instance
      of the sub-class.
      url_key: The url encoded key for an entity in the datastore.
    """
    key = ndb.Key(urlsafe=url_key)
    key.delete()


class User(BaseModel):
  """Datastore service to handle dasher users."""

  email = ndb.StringProperty()
  name = ndb.StringProperty()
  private_key = ndb.TextProperty()
  public_key = ndb.TextProperty()

  @staticmethod
  def _CreateUser(directory_user, key_pair):
    """Create an appengine datastore entity representing a user.

    Args:
      directory_user: A dictionary of the dasher user.

    Returns:
      user_entity: An appengine datastore entity of the user.
    """
    email = directory_user['primaryEmail']
    user_key = ndb.Key(User, hashlib.sha256(email).hexdigest())
    user_entity = User(key=user_key,
                       email=directory_user['primaryEmail'],
                       name=directory_user['name']['fullName'],
                       public_key=key_pair['public_key'],
                       private_key=key_pair['private_key'])
    return user_entity

  @staticmethod
  def _GenerateKeyPair():
    """Generate a private and public key pair in base64.

    Returns:
      key_pair: A dictionary with private_key and public_key in b64 value.
    """
    rsa_key = RSA.generate(2048)
    private_key = base64.urlsafe_b64encode(rsa_key.exportKey())
    public_key = base64.urlsafe_b64encode(rsa_key.publickey().exportKey())

    key_pair = {
      'private_key': private_key,
      'public_key': public_key
    }

    return key_pair

  @staticmethod
  def _UpdateKeyPair(key):
    """Update an existing appengine datastore user entity with a new key pair.

    Args:
      key: A user's key in order to find the user's datastore entity.
    """
    user = User.GetByKey(key)
    key_pair = User._GenerateKeyPair()
    user.public_key=key_pair['public_key']
    user.private_key=key_pair['private_key']
    user.put()

  @staticmethod
  def InsertUser(directory_user, key_pair):
    """Insert a user into datastore.

    Args:
      directory_user: A dictionary of the dasher user.
    """
    user = User._CreateUser(directory_user, key_pair)
    user.put()

  @staticmethod
  def InsertUsers(directory_users):
    """Insert users into datastore.

    Args:
      directory_users: A list of dasher users.
    """
    user_entities = []
    for directory_user in directory_users:
      key_pair = User._GenerateKeyPair()
      user_entities.append(User._CreateUser(directory_user, key_pair))
    ndb.put_multi(user_entities)


class ProxyServer(BaseModel):
  """Store data related to the proxy servers."""

  ip_address = ndb.StringProperty()
  ssh_private_key = ndb.TextProperty()
  fingerprint = ndb.StringProperty()

  @staticmethod
  def Insert(ip_address, ssh_private_key, fingerprint):
    entity = ProxyServer(ip_address=ip_address,
                         ssh_private_key=ssh_private_key,
                         fingerprint=fingerprint)
    entity.put()

  @staticmethod
  def Update(id, ip_address, ssh_private_key, fingerprint):
    entity = ProxyServer.Get(id)
    entity.ip_address = ip_address
    entity.ssh_private_key = ssh_private_key
    entity.fingerprint = fingerprint
    entity.put()

class OAuth(BaseModel):
  """Store the client secret so that it's not checked into source code.

  Secret is accessible at:
  https://console.developers.google.com/project
  Set the secret using the Datastore Viewer at https://appengine.google.com
  """
  CLIENT_SECRET_ID = 'my_client_secret'

  client_id = ndb.StringProperty()
  client_secret = ndb.StringProperty()
  DEFAULT_ID = 'Change me to the real id.'
  DEFAULT_SECRET = 'Change me to the real secret.'

  @staticmethod
  def GetOrInsertDefault():
    # Ensure there's only one key.
    entity = OAuth.Get(OAuth.CLIENT_SECRET_ID)
    if not entity:
      OAuth.InsertDefault()
      entity = OAuth.Get(OAuth.CLIENT_SECRET_ID)
    return entity

  @staticmethod
  def InsertDefault():
    # Ensure there's only one key.
    OAuth.Insert(new_client_id=OAuth.DEFAULT_ID,
                 new_client_secret=OAuth.DEFAULT_SECRET)

  @staticmethod
  def Insert(new_client_id, new_client_secret):
    # Ensure there's only one key.
    entity = OAuth(id=OAuth.CLIENT_SECRET_ID,
                   client_id=new_client_id,
                   client_secret=new_client_secret)
    entity.put()

  @staticmethod
  def Update(new_client_id, new_client_secret):
    # Ensure there's only one key.
    entity = OAuth.Get(OAuth.CLIENT_SECRET_ID)
    entity.client_id=new_client_id
    entity.client_secret=new_client_secret
    entity.put()

  @staticmethod
  def Flush():
    # Make sure to update the memcache
    memcache.flush_all()
