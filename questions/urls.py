from django.conf.urls.defaults import patterns, url
from django.views.generic.list_detail import object_list

urlpatterns = patterns('questions.views',

url(r'^$', 'question_index', name='question_index'),
url(r'^filters/$', 'user_filters', name='user_filters'),

url(r'^(?P<question_id>\d+)/$', 'question', name='question'),
url(r'^(?P<question_id>\d+)/answer/$', 'answers', name='answers'),
url(r'^(?P<question_id>\d+)/userchoice/$', 'userchoice', name='userchoice'),

#url(r'^stats/$', 'question_stats', name='question_stats'),
)