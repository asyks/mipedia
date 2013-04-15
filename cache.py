#!/usr/bin/python

import memcache
import dbm, util
from datetime import datetime

class users:

  def set_user_cache(key, user):
    last_login = datetime.utcnow()
    memcache.set(key, (user, last_login))

  def get_user_cache(key):
    u = memcache.get(key)
    if u:
      user_id, last_login = u
    else:
      user_id, last_login = None, None
    return user_id, last_login

class wikis:

  memc = memcache.Client(['127.0.0.1:11211'], debug=1)

  @classmethod
  def set(cls, k, w):
    try:
      saveTime = datetime.utcnow() 
      return cls.memc.set(str(k), w) 
    except:
      logging.error(error)

  @classmethod
  def get(cls, k):
    try:
      w = cls.memc.get(str(k))
      logging.warning(w)
      return w
    except:
      return None

  @classmethod
  def get_and_add(cls, k, t, v=None):
    wiki = dbm.wiki.select_by_title_and_version(t, v)
    cls.set(key, wiki)
    wiki, saveTime = cls.get(key)
    return wiki, saveTime

  @classmethod
  def wiki_put_and_cache(title, version, content=' '):
    key_one = dbm.wiki.Key.from_path('wiki', title+str(version)) 
    key_two = db.Key.from_path('wiki', title) 
    wiki = Wiki.make_entry(title, version, content)
    wiki.put()
    return wiki

  @classmethod
  def wiki_cache(title, version=None, update=False):
    if version:
      key = db.Key.from_path('wiki', title+str(version)) 
    else:
      key = db.Key.from_path('wiki', title)
      wiki, saveTime = cls.get(str(key))
    if update == True or wiki == None: 
      wiki, saveTime = wiki_get_and_cache(str(key), title, version)
    return wiki, saveTime 
