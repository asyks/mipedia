import web, os, hashlib, jinja2, psycopg2, logging
import route, dbm, util, cache

class Handler:

  def __init__(self):
    self.p = dict()
    self.p['paths'] = route.paths
    self.p['user'] = self.u = self.read_user_cookie()
    if self.u:
      web.session.login = 1
    else:
      web.session.login = 0
    web.header('Content-Type', 'text/html')

  def get_referer(self):
    self.referer = web.ctx.env.get('HTTP_REFERER',
      route.paths.get('index'))

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
    if not util.email_validate(i.email):
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
      raise web.seeother(route.paths.get('index'))

class Login(Handler):

  def GET(self):
    self.get_referer()
    if self.logged():
      web.seeother(self.referer)
    else:
      return self.render('login.html', **self.p)

  def POST(self):
    i = web.input()
    s = self.login(u=i.username, p=i.password)
    raise web.seeother(route.paths.get('index'))

class Logout(Handler):

  def GET(self):
    self.get_referer()
    s = self.logout() 
    raise web.seeother(self.referer)

class WikiRead(Handler):
  
  def GET(self, t):
    self.get_referer()
    i = web.input()
    try:
      v = i.v
    except:
      v = None
    try:
      w = dbm.wikis.select_by_title_and_version(t=t,v=v)[0]
      self.p['title'], self.p['content'], self.p['edited'] = \
        w.title, util.make_md(w.content), w.created
    except:
      if self.u:
        dbm.wikis.insert_one(t=t,u=self.u)
        raise web.seeother('/w/_edit/' + t)
      else:
        raise web.seeother(self.referer)
    return self.render('read.html', **self.p)

class WikiEdit(Handler):

  def GET(self, t):
    self.get_referer()
    if not self.u:
      raise web.seeother(self.referer)
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
      dbm.wikis.insert_one(t=t, u=self.u)
      w = dbm.wikis.select_by_title_and_version(t=t,v=v)[0]
      self.p['title'], self.p['content'], self.p['edited'] = \
        w.title, w.content, w.created
    return self.render('edit.html', **self.p)

  def POST(self, t):
    self.get_referer()
    if not self.u:
      raise web.seeother(self.referer)
    i = web.input()
    c = util.sanitize_html(i.content)
    dbm.wikis.insert_one(t=t, u=self.u, c=c)
    raise web.seeother('/w/%s' % t)

class WikiHist(Handler):

  def GET(self, t):
    self.get_referer()
    if not self.u:
      raise web.seeother(self.referer)
    w = list(dbm.wikis.select_by_title(t=t))
    self.p['page_history'], self.p['title'] = w, t
    return self.render('hist.html', **self.p)

class WikiDisc(Handler):

  def POST(self):
    i = web.input()
    e = i.entry
    raise web.seeother(route.paths.get('wikiread') + e)

urls = (
  route.routes.get('index'), Index,
  route.routes.get('signup'), SignUp,
  route.routes.get('login'), Login,
  route.routes.get('logout'), Logout,
  route.routes.get('wikidisc'), WikiDisc,
  route.routes.get('wikiedit'), WikiEdit,
  route.routes.get('wikihist'), WikiHist,
  route.routes.get('wikiread'), WikiRead
)

web.config.debug = False
app = web.application(urls, globals(), autoreload=True)
web.session.Session(app, web.session.DiskStore('sessions'))
web.session.login = web.session.privilage = 0

if __name__ == "__main__":
  app.run()
