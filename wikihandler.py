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

  def login(self, u, p):
    r = dbm.users.select_by_name(u)[0]
    if r and util.check_hash(u, p, r.get('passwordhash')):
      d = r.get('id')
      self.set_user_cookie(d)
      session.login = 1
    else:
      logging.warning('passwords do not match')
    return session.login

  def logout(self):
    self.remove_user_cookie()
    session.login = 0
    return session.login

  def logged(self):
    return session.login == 1

  def set_user_cookie(self, val):
    secureVal = util.make_secure_val(str(val))
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
      s = self.login(i.username, i.password)
      raise web.seeother(self.lastPage) ## try replace raise w/ return

class Login(Handler):

  def GET(self):
    if self.logged():
      web.seeother(self.lastPage)
    else:
      return self.render('login.html')

  def POST(self):
    i = web.input()
    s = self.login(u=i.username, p=i.password)
    raise web.seeother(self.lastPage)

class Logout(Handler):

  def GET(self):
    s = self.logout() 
    raise web.seeother(self.lastPage)

class WikiRead(Handler):
  
  def GET(self, topic):
    return "Wiki Read page"

PAGE_RE = '(/(?:[a-zA-Z0-9_-]+/?)*)'

urls = (
  '/?', Index,
  '/signup/?', SignUp,
  '/login/?', Login,
  '/logout/?', Logout,
#  '/_edit/' + PAGE_RE, WikiEdit,
#  '/_hist/' + PAGE_RE, WikiHist,
  PAGE_RE, WikiRead
)

if __name__ == "__main__":
  app.run()
