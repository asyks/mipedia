
import web, os, hashlib, jinja2, psycopg2, logging
import dbm, util

class Handler:

  def __init__(self):
    self.lastPage = '/'
    self.p = dict()
    self.p['user'] = self.u = self.read_user_cookie()
    if self.u:
      web.session.login = 1
    else:
      web.session.login = 0
    web.header('Content-Type', 'text/html')

  def login(self, u, p):
    try:
      r = dbm.users.select_by_name(u)[0]
      if r and util.check_hash(u, p, r.get('passwordhash')):
        self.set_user_cookie(u)
        web.session.login = 1
      else:
        logging.warning('passwords do not match')
        web.session.login = 0
    except error:
      logging.warning('there was an error logging in')
      web.session.login = 0
    return web.session.login

  def logout(self):
    self.remove_user_cookie()
    web.session.login = 0
    return web.session.login

  def logged(self):
    return web.session.login == 1

  def set_user_cookie(self, val):
    secureVal = util.make_secure_val(str(val))
    web.setcookie(name='user',value=secureVal,
      expires=3600,secure=False)
  
  def remove_user_cookie(self):
    web.setcookie(name='user',value='',expires=-1,secure=False)

  def read_user_cookie(self):
    cookieValue = web.cookies().get('user')
    return cookieValue and util.check_secure_val(cookieValue)

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
    return self.render('index.html', **self.p)

class SignUp(Handler):

  def GET(self):
    return self.render('signup.html', **self.p)

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
  
  def GET(self, t):
    i = web.input()
    try:
      v = i.v
    except:
      v = None
    try:
      w = dbm.wikis.select_by_title_and_version(t=t,v=v)[0]
      self.p['title'], self.p['content'], self.p['edited'] = \
        w.title, w.content, w.created
    except:
      if self.u:
        dbm.wikis.insert_one(t=t)
        raise web.seeother('/w/_edit/' + t)
      else:
        raise web.seeother(self.lastPage)
    return self.render('read.html', **self.p)

class WikiEdit(Handler):

  def GET(self, t):
    if not self.u:
      raise web.seeother(self.lastPage)
    i = web.input()
    try:
      v = i.v
    except:
      v = None
    try:
      w = dbm.wikis.select_by_title_and_version(t=t,v=v)[0]
      self.p['title'], self.p['content'], self.p['edited'] = \
        w.title, w.content, w.created
    except:
      dbm.wikis.insert_one(t=t)
      w = dbm.wikis.select_by_title_and_version(t=t,v=v)[0]
      self.p['title'], self.p['content'], self.p['edited'] = \
        w.title, w.content, w.created
    return self.render('edit.html', **self.p)

  def POST(self, t):
    if not self.u:
      raise web.seeother(self.lastPage)
    i = web.input()
    c = i.content
    dbm.wikis.insert_one(t=t, c=c)
    raise web.seeother('/w/%s' % t)

class WikiHist(Handler):

  def GET(self, t):
    if not self.u:
      raise web.seeother(self.lastPage)
    w = list(dbm.wikis.select_by_title(t=t))
    self.p['page_history'], self.p['title'] = w, t
    return self.render('hist.html', **self.p)

PAGE_RE = '((?:[a-zA-Z0-9_-]+))'
urls = (
  '/?', Index,
  '/a/signup/?', SignUp,
  '/a/login/?', Login,
  '/a/logout/?', Logout,
  '/w/_edit/' + PAGE_RE + '/?', WikiEdit,
  '/w/_hist/' + PAGE_RE + '/?', WikiHist,
  '/w/' + PAGE_RE + '/?', WikiRead
)
web.config.debug = False
app = web.application(urls, globals(), autoreload=True)
web.session.Session(app, web.session.DiskStore('sessions'))
web.session.login = web.session.privilage = 0

if __name__ == "__main__":
  app.run()
