from django.conf.urls.defaults import *
import radprofile.views

urlpatterns = patterns("radprofile.views",
    url(r"^$", radprofile.views.ProfileListView.as_view(), name="profile_list"),
    url(r"^profile/(?P<slug>[\w\._-]+)/$", radprofile.views.ProfileDetailView.as_view(), name="profile_detail"),
    url(r"^user_profile/(?P<username>[\w\._-]+)/$", "user_profile", name="user_profile"),
#    url(r"^edit/$", "profile_edit", name="profile_edit"),
    url(r"^edit/$", radprofile.views.ProfileView.as_view(), name="profile_edit"),
)
