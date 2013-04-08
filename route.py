#!/usr/bin/python

PAGE_RE = '((?:[a-zA-Z0-9_-]+))'

paths = dict(
  index = '/?',
  signup = '/a/signup/?',
  login = '/a/login/?',
  logout = '/a/logout/?',
  wikiread = '/w/%s/?' % PAGE_RE,
  wikiedit = '/w/_edit/%s/?' % PAGE_RE,
  wikihist = '/w/_hist/%s/?' % PAGE_RE
)
