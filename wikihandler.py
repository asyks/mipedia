import web
import os
import jinja2

class Handler:

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
    name = 'user_id'
    secret_key = make_secure_val(val)
    web.config.session_parameters['cookie_name'] = name
    web.config.session_parameters['secret_key'] = secret_key

class index(Handler):

  def GET(self):
    return self.render('index.html')

PAGE_RE = '(/(?:[a-zA-Z0-9_-]+/?)*)'

urls = (
  '/', 'index'#,
#  '/login/?', Login,
#  '/logout/?', Logout,
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
