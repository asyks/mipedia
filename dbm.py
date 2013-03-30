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
    db.select('users')

  @classmethod
  def select_by_name(cls, u):
    db.select('users', where="username='%s'" % u)

  @classmethod
  def select_by_id(cls, i):
    db.select('users', where='id=%s' % i)
