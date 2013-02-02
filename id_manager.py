# TODO this stuff needs to be switched to redis and made threadsafe

import base64
import struct

class IdManager():
  def __init__(self):
    self._next_id = 0
    self._id_to_kwargs = {}

  def get_next_id(self):
    self._next_id += 1
    return self.__encode(self._next_id)

  def save(self, page_id, args):
    # TODO not checking for duplicate args
    self._id_to_kwargs[page_id] = args

  def get_kwargs(self, page_id):
    if page_id not in self._id_to_kwargs:
      return None
    return self._id_to_kwargs[page_id]

  def __encode(self, n):
    return base64.b64encode(str(n)).rstrip('=')
