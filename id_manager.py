import base64
import redis
import json
from pymongo import MongoClient

REDIS_PREFIX = "conspiracy:pages:"
REDIS_PAGEID_PREFIX = "conspiracy:pages:id:"

REMOTE_REDIS_HOST = '10.151.12.22'

class IdManager():
  def __init__(self):
    self._next_id = 0
    self._id_to_kwargs = {}
    self._redis = redis.StrictRedis(host='localhost', port=6379, db=1)
    self._remote_redis = redis.StrictRedis(host=REMOTE_REDIS_HOST, port=6379, db=1)

    self._mongo = MongoClient()
    db = self._mongo.verified_facts
    self._mongo_coll = db.articles
    self._mongo_coll.ensure_index('permalink_id', unique=True)

    print 'IdManager initialized with', self._mongo_coll.count(), 'articles'

  def get_next_id(self):
    next_id = self._redis.incr(REDIS_PREFIX + 'next_id')
    return self.__encode(next_id)

  def save(self, page_id, args):
    # note that we don't check for duplicate args
    self._id_to_kwargs[page_id] = args

    json_args = json.dumps(args)

    # Storing in mongo
    json_args['permalink_id'] = page_id
    self._mongo_coll.insert(json_args)

    # store in remote from now on; local is out of space
    #self._remote_redis.set(REDIS_PAGEID_PREFIX + str(page_id), json_args)

  def get_kwargs(self, page_id):
    ret = self.__mongo_lookup(page_id)
    if ret:
      return ret

    # Lookup in redis for backwards compatibility
    return self.__redis_lookup(page_id)

  def __mongo_lookup(self, page_id):
    return self._mongo_coll.find_one({'permalink_id': page_id})

  def __redis_lookup(self, page_id):
    json_args = self._redis.get(REDIS_PAGEID_PREFIX + str(page_id))
    if not json_args:
      # try from remote
      json_args = self._remote_redis.get(REDIS_PAGEID_PREFIX + str(page_id))
      if not json_args:
        return None
    return json.loads(json_args)

  def __encode(self, n):
    return base64.b64encode(str(n)).rstrip('=')
