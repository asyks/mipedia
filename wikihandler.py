import web
import os
import jinja2
import logging
from utility import *

class Handler:

  def __init__(self):
    self.lastPage = '/'
    user = self.read_user_cookie()
#    if user is None:
#      self.set_user_cookie('aaron')
#      user = self.read_user_cookie()
    logging.warning(user)

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

  def set_user_cookie(self, val):
    secretKey = make_secure_val(val)
    web.setcookie(name='user_id',
      value=secretKey, 
      expires=3600,
      secure=False)
  
  def remove_user_cookie(self):
    logging.warning('remove user cookie')
    web.setcookie(name='user_id',
      value='', 
      expires=-1,
      secure=False)

  def read_user_cookie(self):
    cookieValue = web.cookies().get('user_id')
    return cookieValue and check_secure_val(cookieValue)

class index(Handler):

  def GET(self):
    return self.render('index.html')

class Login(Handler):

  def GET(self):
    return self.render('login-form.html')

  def POST(self):
    params = web.data()
    paramDict = dict()
    make_dict_from_params(params, paramDict)
    self.set_user_cookie(val=paramDict.get('username'))
    web.seeother(self.lastPage)

class Logout(Handler):

  def GET(self):
    self.remove_user_cookie()
    web.seeother(self.lastPage)

PAGE_RE = '(/(?:[a-zA-Z0-9_-]+/?)*)'

urls = (
  '/', 'index',
  '/login/?', Login ,
  '/logout/?', Logout#,
#  '/signup/?', Singup,
#  '/_edit/?' + PAGE_RE, EditPage,
#  '/_history' + PAGE_RE, History,
#  PAGE_RE, WikiPage
)

if __name__ == "__main__":
  app = web.application(urls, globals())
  app.run()
  app = web.application(urls, locals())
  session = web.session.Session(app, web.session.DiskStore('sessions'), initializer={'count': 0})
