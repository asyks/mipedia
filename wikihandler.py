import web, os, hashlib, logging
import jinja2, psycopg2
#from db import *
import dbm, util
#from utility import *

web.config.debug = False
app = web.application(urls, globals())
store = web.session.DBStore(db, 'sessions')
session = web.session.Session(app, store)
session.login = session.privilage = 0

class Handler:

  def __init__(self):
    self.lastPage = '/'
    self.p = dict()
    user = self.read_user_cookie()
    logging.warning(user)
    if user:
      session.login = 1
    else:
      session.login = 0

  def login(self, d=None, u=None):
    if not d:
      try:
        d = dbm.users.select_by_name(u).get('id')
      except AttributeError:
        web.seeother(self.lastPage)
    self.set_user_cookie(d)
    session.login = 1
    return session.login

  def logout(self):
    self.remove_user_cookie()
    session.login = 0
    session.kill()
    return 0

  def logged(self):
    if session.login == 1:
      return True
    else:
      return False

  def set_user_cookie(self, val):
    secureVal = util.make_secure_val(val)
    web.setcookie(name='user',value=secureVal,
      expires=3600,secure=False)
  
  def remove_user_cookie(self):
    web.setcookie(name='user',value='',expires=-1,secure=False)

  def read_user_cookie(self):
    cookieValue = web.cookies().get('user')
    return cookieValue and check_secure_val(cookieValue)

  def render(self, templateName, **context):
    extensions = context.pop('extensions', [])
    globals = context.pop('globals', {})
    path = os.path.dirname(__file__)
    templates = os.path.join(path, 'templates')
    loader = jinja2.FileSystemLoader(templates)
    jinja_env = jinja2.Environment(loader=loader, 
      autoescape=True,
      extensions=extensions)
    return jinja_env.get_template(templateName).render(context)

class Index(Handler):

  def GET(self):
    return self.render('index.html')

class SignUp(Handler):

  def GET(self):
    return self.render('signup.html')

  def POST(self):
    i = web.input()
    have_error = False
    if not util.user_validate(i.username):
      have_error = True
      self.p['errorUsername'] = 'Invalid Username'
    elif dbm.users.select_by_name(i.username):
      have_error = True
      self.p['errorUsername'] = 'Username already taken'
    if not util.password_validate(i.password):
      have_error = True
      self.p['errorPassword'] = 'Invalid Password'
    elif not util.password_verify(i.password, i.verify):
      have_error = True
      self.p['errorPassword'] = 'Passwords don\'t match'
    if not email_validate(i.email):
      have_error=True
      self.p['errorEmail'] = 'email address not valid'
    elif dbm.users.select_by_email(i.email):
      have_error=True
      self.p['errorEmail'] = 'email address already taken'
    if have_error:
      self.p['username'], self.p['email'] = i.username, i.email
      return self.render('signup.html', **self.p)
    else:
      dbm.users.insert_one(u=i.username, p=i.password, e=i.email)
      s = self.login()
      raise web.seeother(self.lastPage) ## try replace raise w/ return

class Login(Handler):

  def GET(self):
    if self.logged():
      web.seeother(self.lastPage)
    else:
      return self.render('login-form.html')

  def POST(self):
    i = web.input()
    s = self.login(u=i.username)
    raise web.seeother(self.lastPage)

class Logout(Handler):

  def GET(self):
    s = self.logout 
    raise web.seeother(self.lastPage)

PAGE_RE = '(/(?:[a-zA-Z0-9_-]+/?)*)'

urls = (
  '/', Index,
  '/login/?', Login,
  '/logout/?', Logout,
  '/signup/?', SignUp
)

if __name__ == "__main__":
  app.run()
