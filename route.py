#!/usr/bin/python

PAGE_RE = '((?:[a-zA-Z0-9_-]+))'

paths = dict(
  index    = '/',
  signup   = '/a/signup',
  login    = '/a/login',
  logout   = '/a/logout',
  wikiread = '/w/',
  wikiedit = '/w/_edit/',
  wikihist = '/w/_hist/',
  wikidisc = '/w/_disc'
)

routes = dict(
  index    = paths.get('index') + '?',
  signup   = paths.get('signup') + '/?',
  login    = paths.get('login') + '/?',
  logout   = paths.get('logout') + '/?',
  wikiread = paths.get('wikiread') + PAGE_RE + '/?',
  wikiedit = paths.get('wikiedit') + PAGE_RE + '/?',
  wikihist = paths.get('wikihist') + PAGE_RE + '/?',
  wikidisc = paths.get('wikidisc') + '/?'
)
