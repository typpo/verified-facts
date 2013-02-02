# TODO this stuff needs to be switched to redis and made threadsafe

import base64
import redis
import json

REDIS_PREFIX = "conspiracy:pages:"
REDIS_PAGEID_PREFIX = "conspiracy:pages:id:"

class IdManager():
  def __init__(self):
    self._next_id = 0
    self._id_to_kwargs = {}
    self._redis = redis.StrictRedis(host='localhost', port=6379, db=1)

    # load in existing pages
    pagekeys = self._redis.keys(REDIS_PAGEID_PREFIX + '*')
    self.first_time = len(pagekeys) < 1
    print 'Loaded %d existing keys' % (len(pagekeys))

  def get_next_id(self):
    next_id = self._redis.incr(REDIS_PREFIX + 'next_id')
    return self.__encode(next_id)

  def save(self, page_id, args):
    # note that we don't check for duplicate args
    self._id_to_kwargs[page_id] = args

    json_args = json.dumps(args)
    self._redis.set(REDIS_PAGEID_PREFIX + str(page_id), json_args)

  def get_kwargs(self, page_id):
    json_args = self._redis.get(REDIS_PAGEID_PREFIX + str(page_id))
    if not json_args:
      return None
    return json.loads(json_args)

  def __encode(self, n):
    return base64.b64encode(str(n)).rstrip('=')
