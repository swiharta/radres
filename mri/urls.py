from django.conf.urls.defaults import patterns, url#, include
# from django.views.generic.simple import direct_to_template
from .views import MRIView

urlpatterns = patterns('',
  url(r'^$', MRIView.as_view(), name='mri_protocol_index'),
  url(r'(.+\.html)$', 'django.views.generic.simple.direct_to_template'),
  )