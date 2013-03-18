import web, jinja2

path = os.path.dirname(__file__)
templates = os.path.join(path, 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(templates), autoescape=True)
last_page = '/'

class Handler:

  ## this function might replace all 3 write/render functions
  ## in the GAE mickipebia app
  def render(self, template, **kw):
    template = jinja_env.get_template(template)
    print template.render(**kw)

  def set_user_cookie(self, val):
    name = 'user_id'
    secret_key = make_secure_val(val)
    web.config.session_parameters['cookie_name'] = name
    web.config.session_parameters['secret_key'] = secret_key

class index:
  def GET(self):
    return "Hello, World!"

PAGE_RE = '(/(?:[a-zA-Z0-9_-]+/?)*)'

urls = (
  '/', 'index',
  '/login/?', Login,
  '/logout/?', Logout,
  '/signup/?', Singup,
  '/_edit/?' + PAGE_RE, EditPage,
  '/_history' + PAGE_RE, History,
  PAGE_RE, WikiPage
)

if __name__ == "__main__":
  app = web.application(urls, globals())
  app.run()
  app = web.application(urls, locals())
  session = web.session.Session(app, web.session.DiskStore('sessions'), initializer={'count': 0})
