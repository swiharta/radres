import os
import sys

from os.path import abspath, dirname, join
from site import addsitedir

addsitedir('/home/swihart/env/pinax09a1/lib/python2.7/site-packages')
sys.path.insert(0, abspath(join(dirname(__file__), "../../")))

from django.conf import settings
os.environ["DJANGO_SETTINGS_MODULE"] = "radres.settings"

#sys.path.insert(0, join(settings.PROJECT_ROOT, "apps"))
sys.path.insert(0, settings.PROJECT_ROOT)

from django.core.handlers.wsgi import WSGIHandler
application = WSGIHandler()
