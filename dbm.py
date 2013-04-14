#!/usr/bin/python

import web, psycopg2, logging
import util, cache

db = web.database(dbn='postgres', user='aaron',
  pw='gimmie some sql', db ='wiki1')

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
    return db.select('wikis', vars=dict(t=t), where='title=$t', 
      order='created DESC')

  @classmethod
  def select_by_title_and_version(cls, t, v=None):
    if v is None:
      return db.query('SELECT * FROM wikis WHERE title=$t AND\
        version=(SELECT max(version) FROM wikis WHERE title=$t)',
        vars=dict(t=t))
    else:
      return db.select('wikis', vars=dict(t=t,v=v), 
        where='title=$t and version=$v')
