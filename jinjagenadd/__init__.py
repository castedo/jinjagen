import datetime, markdown
from jinja2 import Markup, contextfunction

def index2dot(path):
  ok = (path != 'index.html' and path[-11:] != '/index.html')
  return path if ok else path[:-10] + '.'

marker = markdown.Markdown()

def markdown(txt):
  output = marker.convert(txt)
  marker.reset()
  return Markup(output + "\n")

@contextfunction
def include_raw(ctx,name):
  output = ctx.environment.loader.get_source(ctx.environment, name)[0]
  return Markup(output)

def jinjagen_hook(generator, param):
  generator.env.filters.update({
    'index2dot': index2dot,
    'markdown': markdown,
    'dateformat': lambda v, f="%Y-%m-%d": v.strftime(f)
  })
  generator.env.globals.update({
    'flags': param.split(',') if param else [],
    'today': datetime.datetime.today,
    'include_raw': include_raw,
    'import': lambda path: generator.env.get_template(path).module,
    'list_templates': lambda prefix='': generator.list_gen_templates(prefix),
  })

