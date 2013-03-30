import web, os, hashlib, logging
import jinja2, psycopg2
#from db import *
import dbm, util
#from utility import *

web.config.debug = False

db = web.database(dbn='postgres',
    user='aaron', pw='gimmie some sql', db='wiki1')

app = web.application(urls, globals())
store = web.session.DiskStore('sessions')
session = web.session.Session(app, store,
  initializer={'login': 0, 'privilege': 0})

class Handler:

  def __init__(self):
    self.lastPage = '/'
    self.params = dict()
#    user = self.read_user_cookie()
#    if user is None:
#      self.set_user_cookie('aaron')
#      user = self.read_user_cookie()

  def logged(self):
    if session.login == 1:
      return True
    else:
      return False

  def set_user_session(self):
    session.login = 1

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

  def set_user_cookie(self, cookieName, val):
    secureVal = util.make_secure_val(val)
    web.setcookie(name=cookieName,value=secureVal,
      expires=3600,secure=False)
  
  def remove_user_cookie(self, cookieName):
    web.setcookie(name=cookieName,value='',expires=-1,secure=False)

  def read_user_cookie(self, cookieName):
    cookieValue = web.cookies().get(cookieName)
    return cookieValue and check_secure_val(cookieValue)

class Index(Handler):

  def GET(self):
    return self.render('index.html')

class SignUp(Handler):

  def GET(self):
    return self.render('signup-form.html')

  def POST(self):
    i = web.input()
    have_error = False
    if not util.user_validate(i.username):
      have_error = True
      self.params['errorUsername'] = 'Invalid Username'
    elif not dbm.users.select_by_name(i.username):
      have_error = True
      self.params['errorUsername'] = 'Username already taken'
    
    if have_error:
#    logging.warning('%s, %s, %s, %s' % (i.username, i.password, 
#      i.verify, i.email))
      dbm.users.insert_one(u=i.username, p=i.password, e=i.email)
      raise web.seeother(self.lastPage) ## try replace raise w/ return

class Login(Handler):

  def GET(self):
    try:
      if self.logged():
        logging.warning('already logged in log out first')
        web.seeother(lastPage)
      else:
        return self.render('login-form.html')
    except:
      return self.render('login-form.html')

  def POST(self):
    i = web.input()
    util.check_hash(i.username, i.password)
    raise web.seeother(self.lastPage)

class Logout(Handler):

  def GET(self):
    self.remove_user_cookie()
    raise web.seeother(self.lastPage)

PAGE_RE = '(/(?:[a-zA-Z0-9_-]+/?)*)'

urls = (
  '/', index,
  '/login/?', Login,
  '/logout/?', Logout,
  '/signup/?', SignUp
)

if __name__ == "__main__":
  app.run()
