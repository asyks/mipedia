#!/usr/bin/python

import hashlib, hmac, string, random, re
import logging
from datetime import datetime

## deprecated method for making a dict out of a web.data() return str
def make_dict_from_params(params, paramDict):
  params = params.split('&')
  for param in params:
    paramPair = param.split('=')
    paramDict[paramPair.pop()] = paramPair.pop()

## sign-up form validation stuff
USER_RE = re.compile("^[a-zA-Z0-9_-]{3,20}$")
PASS_RE = re.compile("^.{3,20}$")
EMAIL_RE = re.compile("^[\S]+@[\S]+\.[\S]+$")

def user_validate(u):
  if USER_RE.match(u):
    return True

def password_validate(p):
  if PASS_RE.match(p):
    return True

def password_verify(p,v):
  if p == v:
    return True

def email_validate(e): 
  if not e:
    return True
  if e and EMAIL_RE.match(e):
    return True

## cookie setting procedures
secret = 'you will never be able to guess me'

def make_secure_val(val):
  return '%s|%s' % (val, hmac.new(secret, val).hexdigest())

def check_secure_val(secure_val):
  val = secure_val.split('|')[0]
  if secure_val == make_secure_val(val):
    return val 

## password hashing  procedures
def make_salt():
  return ''.join(random.choice(string.letters) for x in range(5))

def make_hash(un, pw, salt=None):
  if not salt:
    salt = make_salt()
  h = hashlib.sha256(un + pw + salt).hexdigest()
  return '%s|%s' % (salt, h)

def check_hash(un, pw, h):
  h = string.rstrip(h) ## if I adjust psql users table I won't need it
  salt = h.split('|')[0]
  if h == make_hash(un, pw, salt):
    return True
