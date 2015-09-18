"""Module to interact with datastore models and helper functions."""

import hashlib

from google.appengine.ext import ndb


class User(ndb.Model):
  """Users from the dasher domain or account."""

  email = ndb.StringProperty()
  name = ndb.StringProperty()

  @staticmethod
  def _Create(directory_user):
    entity_id = hashlib.sha256(directory_user['primaryEmail']).hexdigest()
    user_entity = User(key=ndb.Key(User, entity_id))
    user_entity.email = directory_user['primaryEmail']
    user_entity.name = directory_user['name']['fullName']
    return user_entity

  @staticmethod
  def Insert(directory_user):
    ndb.put(User._Create(directory_user))

  @staticmethod
  def InsertMany(directory_users):
    user_entities = []
    for directory_user in directory_users:
      user_entities.append(User._Create(directory_user))
    ndb.put_multi(user_entities)

  @staticmethod
  def Get(email):
    entity_id = hashlib.sha256(email).hexdigest()
    return User.get_by_id(entity_id)

  @staticmethod
  def GetUsers():
    q = User.query()
    return q.fetch()
  
  @staticmethod
  def GetCount():
    q = User.query()
    return q.count()


class OAuth(ndb.Model):
  """Store the client secret so that it's not checked into source code.

  Secret is accessible at:
  https://console.developers.google.com/project
  Set the secret using the Datastore Viewer at https://appengine.google.com
  """
  CLIENT_SECRET_ID = 'my_client_secret'

  client_secret = ndb.StringProperty()

  @staticmethod
  def GetSecret():
    # Ensure there's only one key.
    entity = OAuth.get_by_id(OAuth.CLIENT_SECRET_ID)
    if not entity:
      entity = OAuth(id=OAuth.CLIENT_SECRET_ID,
                     client_secret='Change me to the real secret.')
      entity.put()
    return entity.client_secret
