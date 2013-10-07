#from django.conf import settings
#from django.core.exceptions import ImproperlyConfigured
#from django.contrib.auth.models import User


_inbox_count_sources = None

def resolve_url_name(request):
  """Allows us to see what the matched urlname for this
  request is within the template"""
  from django.core.urlresolvers import resolve
  try:
    res = resolve(request.path)
    if res:
      print res.url_name
      return {'url_name' : res.url_name}
    else:
      return {}
  except:
    return {}