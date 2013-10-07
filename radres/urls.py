from django.conf import settings
from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template, redirect_to
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static
# from staticfiles.urls import staticfiles_urlpatterns

from django.contrib import admin
from ajax_select import urls as ajax_select_urls

admin.autodiscover()
# for django-moderation
#from moderation.helpers import auto_discover
#auto_discover()
# endfor django-moderation
from tastypie.api import Api

import radprofile.views as radprofile_views
import account.views as account_views


v1_api = Api()
from radprofile.resources import *
v1_api.register(ProfileResource())
v1_api.register(UserResource())
v1_api.register(GroupResource())

from radcal.resources import *
v1_api.register(ShiftEventResource())
v1_api.register(ConfEventResource())
v1_api.register(ConferenceResource())
v1_api.register(ShiftResource())
v1_api.register(EventFilterResource())
v1_api.register(ShiftTradeResource())

from taxonomy.resources import *
v1_api.register(EventFilterResource())
v1_api.register(SubspecialtyResource())

urlpatterns = patterns("",

    url(r'^api/', include(v1_api.urls)),
    url(r"^$", 'radcal.views.home', name='home'),
	url(r'^favicon\.ico$', redirect_to, {'url': '/site_media/static/favicon.ico'}),
    url(r"^events\.ics$", direct_to_template, { "template": "events.ics", 'mimetype': 'text/calendar'}, ),
    url(r"^mri-intensity/$", direct_to_template, { "template": "mri-intensity.html", }, name="mri"),
    url(r"^mri/", include('mri.urls')),
    url(r"^fluoro-protocols/$", direct_to_template, { "template": "fluoro-protocols.html", }, name="fluoro"),
    url(r"^robots\.txt$", direct_to_template, {
        "template": "robots.txt", 'mimetype': 'text/plain'}, ),
    url(r'^admin/lookups/', include(ajax_select_urls)),
    url(r"^admin/", include(admin.site.urls)),
    url(r"^account/password/reset/$", radprofile_views.PasswordResetView.as_view(), name="account_password_reset"),
    url(r"^account/settings/$", radprofile_views.SettingsView.as_view(), name="account_settings"),
    url(r"^account/login/$", account_views.LoginView.as_view(), name="account_login"),
    url(r"^account/logout/$", account_views.LogoutView.as_view(), name="account_logout"),
    url(r"^account/", include("account.urls")),
    url(r"^i18n/", include("django.conf.urls.i18n")),
    url(r"^avatar/", include("avatar.urls")),
	  url(r'^polls/', include('polls.urls')),
	  url(r'^calendar/', include('radcal.urls')),
    url(r'^profiles/', include('radprofile.urls')),
	  url(r'^questions/', include('questions.urls')),
  
  # for django-memcached
    url(r'^cache/', include('django_memcached.urls')),
)

if settings.DEBUG:
  # add one of these for every non-static root you want to serve
  urlpatterns+= static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
  # this take cares of static media (i.e. bundled in apps, and specified in settings)
  urlpatterns+= staticfiles_urlpatterns()