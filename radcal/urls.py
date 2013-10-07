from django.conf.urls import patterns, url, include
from radcal.views import UserEvents

urlpatterns = patterns('radcal.views',
	
	url(r'^$', 'cal_index', name='cal_index'),
	url(r'conf/$', 'fullcal', name='fullcal'),
	url(r'call/$', 'call', name='call'),
	url(r'list/$', 'shift_table', name='shift_table'),
	url(r'filters/$', 'cal_filters', name='cal_filters'),
	url(r'switches/$', 'cal_switches', name='cal_switches'),
	url(r'residents/$', 'cal_residents', name='cal_residents'),
	url(r'shifts/event/(?P<event_id>\d+)/$', 'shift_event', name='shift_event'),
  url(r'conferences/$', 'conferences', name='conferences'),
  url(r'(?P<username>\w+)/$', UserEvents()),
#  url(r'^(?P<year>\d{4})/$', 'year_archive', name='year_archive'),
#  url(r'^(?P<year>\d{4})/(?P<month>\d{2})/$', 'month_index', name='month_index'),
#  url(r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/$', 'year_index', name='year_index'),

#  url(r'change/$', 'cal_change', name='cal_change'),
	# url(r'^call/$', 'cal_call', name='cal_call'),
	# url(r'^conferences/$', 'cal_conf', name='cal_conf'),
	)

