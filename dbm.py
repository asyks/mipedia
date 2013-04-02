#!/usr/bin/python

import web, psycopg2
import util

db = web.database(dbn='postgres', user='aaron',
  pw='gimmie some sql', db ='wiki1')

class users:

  @classmethod
  def insert_one(cls, u, p, e):
    h = util.make_hash(u, p)
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
  def insert_one(cls, t, v=None, c=''):
    if v:
      db.insert('wikis', title=t, version=v, content=c)
    else:
      db.insert('wikis', title=t, content=c)

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
      v = 0
    return db.select('wikis', vars=dict(t=t,v=v), 
        where='title=$t and version=$v')
