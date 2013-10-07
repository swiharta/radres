from django.conf.urls.defaults import *
#from django.views.generic.simple import direct_to_template

urlpatterns = patterns('polls.views',
	url(r'^$', 'index', name='polls_index'),
	url(r'^poll/(?P<slug>[^\.^/]+)/$', 'question', name='polls_question'),
	url(r'^results/(?P<slug>[^\.^/]+)/$', 'results', name='polls_results'),
	url(r'^create/$', 'create', name='polls_create'),
	url(r'^help/$', 'help', name='polls_help'),
    )