"""Module to interact with datastore models and helper functions.

TODO(henry): Refactor the common methods (get, insert, delete) into base class.
"""

from google.appengine.api import memcache
from google.appengine.ext import ndb


class BaseModel(ndb.Model):
  
  @classmethod
  def GetCount():
    """Get a count of all the entities in the datastore.

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

    Returns:
      A datastore entity.
    """
    return cls.get_by_id(id)

  
class User(BaseModel):
  """Datastore service to handle dasher users."""

  email = ndb.StringProperty()
  name = ndb.StringProperty()

  @staticmethod
  def _CreateUser(directory_user):
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
                       name=directory_user['name']['fullName'])
    return user_entity

  @staticmethod
  def InsertUser(directory_user):
    """Insert a user into datastore.

    Args:
      directory_user: A dictionary of the dasher user.
    """
    ndb.put(User._CreateUser(directory_user))

  @staticmethod
  def InsertUsers(directory_users):
    """Insert users into datastore.

    Args:
      directory_users: A list of dasher users.
    """
    user_entities = []
    for directory_user in directory_users:
      user_entities.append(User._CreateUser(directory_user))
    ndb.put_multi(user_entities)

  # TODO(ethan): Move this into the base model when removing
  # the token datastore.
  @staticmethod
  def DeleteUser(email):
    """Delete a user and his tokens from the datastore.

    Args:
      email: A string of the user email.
    """
    keys_to_be_deleted = []

    user_key = ndb.Key(User, hashlib.sha256(email).hexdigest())
    keys_to_be_deleted.append(user_key)

    token_keys = Token.GetTokenKeys(email)
    keys_to_be_deleted += token_keys

    ndb.delete_multi(keys_to_be_deleted)


class Token(ndb.Model):
  """Datastore service to handle access tokens."""

  private_key = ndb.TextProperty()
  public_key = ndb.TextProperty()

  @staticmethod
  def InsertToken(email, key_pair):
    """Insert a token into datastore.

    Args:
      email: A string of the user email.
      key_pair: A dictionary with private_key and public_key in b64 value.
    """
    # Hashing the public_key as the Token key name because it allows
    # deterministic retrieval and it's the only kind of string representation
    # that's under 500 bytes.
    token_key = ndb.Key(
        User, hashlib.sha256(email).hexdigest(),
        Token, hashlib.sha256(key_pair['public_key']).hexdigest())

    token = Token(key=token_key,
                  public_key=key_pair['public_key'],
                  private_key=key_pair['private_key'])
    token.put()

  @staticmethod
  def DeleteToken(email, public_key):
    """Delete a token from datastore.

    Args:
      email: A string of the user email.
      public_key: A string of the public_key.
    """
    token_key = ndb.Key(
        User, hashlib.sha256(email).hexdigest(),
        Token, hashlib.sha256(public_key).hexdigest())
    token_key.delete()

  @staticmethod
  def GetTokenKeys(email):
    """Get only the datastore keys of the tokens.

    Args:
      email: A string of the user email.

    Returns:
      A list of token key objects for the user.
    """
    user_key = ndb.Key(User, hashlib.sha256(email).hexdigest())
    q = Token.query(ancestor=user_key)
    return q.fetch(keys_only=True)

  @staticmethod
  def GetTokens(email):
    """Get the token entities from datastore.

    Args:
      email: A string of the user email.

    Returns:
      A list of the user's token entities from the datastore.
    """
    user_key = ndb.Key(User, hashlib.sha256(email).hexdigest())
    q = Token.query(ancestor=user_key)
    return q.fetch()

  @staticmethod
  def GetToken(email, public_key):
    """Get a token entity from datastore.

    Args:
      email: A string of the user email.
      public_key: A public key of the token to be retrieved.

    Returns:
      user: A datastore entity of the user who owns the token.
      token: A datastore entity of the token.
    """
    token_key = ndb.Key(
      User, hashlib.sha256(email).hexdigest(),
      Token, hashlib.sha256(public_key).hexdigest())

    token = token_key.get()
    user = token_key.parent().get()

    return user, token


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


class OAuth(ndb.Model):
  """Store the client secret so that it's not checked into source code.

  Secret is accessible at:
  https://console.developers.google.com/project
  Set the secret using the Datastore Viewer at https://appengine.google.com
  """
  CLIENT_SECRET_ID = 'my_client_secret'

  client_secret = ndb.StringProperty()
  client_id = ndb.StringProperty()

  @staticmethod
  def GetSecret():
    entity = OAuth.GetEntity()
    return entity.client_secret

  @staticmethod
  def GetClientId():
    entity = OAuth.GetEntity()
    return entity.client_id

  @staticmethod
  def GetEntity():
    # Ensure there's only one key.
    entity = OAuth.get_by_id(OAuth.CLIENT_SECRET_ID)
    if not entity:
      OAuth.SetDefaultEntity()
      entity = OAuth.get_by_id(OAuth.CLIENT_SECRET_ID)
    return entity

  @staticmethod
  def SetDefaultEntity():
    # Ensure there's only one key.
    entity = OAuth(id=OAuth.CLIENT_SECRET_ID,
                   client_id='Change me to the real id.',
                   client_secret='Change me to the real secret.')
    entity.put()

  @staticmethod
  def SetEntity(client_id, client_secret):
    # Ensure there's only one key.
    entity = OAuth(id=OAuth.CLIENT_SECRET_ID,
                   client_id=client_id,
                   client_secret=client_secret)
    entity.put()

  @staticmethod
  def Flush():
    # Make sure to update the memcache
    memcache.flush_all()
