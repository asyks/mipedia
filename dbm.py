#!/usr/bin/python

import web, psycopg2, logging
import util, cache

#db = web.database(dbn='postgres', user='aaron',
#  pw='gimmie some sql', db ='wiki1')

db = web.database(dbn='postgres', user='quiyctuhkrcjqx',
  pw='wyIdssBQ6tPveIYr35AWdRP8m8', db ='d761e3fpm7nemi',
  host='ec2-107-21-101-4.compute-1.amazonaws.com', port='5432')

class users:

  @classmethod
  def insert_one(cls, u, p, e):
    h = util.make_hash(u, p)
    with db.transaction():
      db.insert('users', username=u, passwordhash=h, email=e)

  @classmethod
  def select_all(cls):
    return db.select('users')

  @classmethod
  def select_by_id(cls, d):
    return db.select('users', vars=dict(d=d), where='id=$d')

  @classmethod
  def select_by_name(cls, u):
    return db.select('users', vars=dict(u=u), where='username=$u')

  @classmethod
  def select_by_email(cls, e):
    return db.select('users', vars=dict(e=e), where='email=$e')

class wikis:

  @classmethod
  def insert_one(cls, t, u, c=''):
    try:
      with db.transaction():
        v = db.query('SELECT max(version) AS maxversion \
          from wikis where title=$t', vars=dict(t=t))[0].maxversion
        v += 1
        db.insert('wikis', title=t, version=v, content=c, username=u)
    except:
      with db.transaction():
        db.insert('wikis', title=t, content=c, username=u)
      
  @classmethod
  def select_all(cls):
    return db.select('wikis', order='created DESC')

  @classmethod
  def select_by_title(cls, t):
    w = cache.wikis.get(t)
    if not w:
      w = db.select('wikis', vars=dict(t=t), where='title=$t', 
        order='created DESC')
      logging.warning(w)
      success = cache.wikis.set(t, w)
    return w

  @classmethod
  def select_by_title_and_version(cls, t, v=None):
    if v is None:
      w = cache.wikis.get(t)
      logging.warning(w)
      if not w:
        w = db.query('SELECT * FROM wikis WHERE title=$t AND\
          version=(SELECT max(version) FROM wikis WHERE title=$t)',
          vars=dict(t=t))
        logging.warning(w)
        success = cache.wikis.set(t, w)
        logging.warning(success)
    else:
      w = db.select('wikis', vars=dict(t=t,v=v), 
        where='title=$t and version=$v')
    return w
