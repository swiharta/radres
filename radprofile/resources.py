from django.contrib.auth.models import User
# from django.db.models import Q
from tastypie.authentication import Authentication, BasicAuthentication
from tastypie.authorization import DjangoAuthorization, Authorization
from tastypie.validation import Validation
from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from .models import Profile
from tastypie import fields
# from tastypie.cache import SimpleCache
# #from tastypie.bundle import Bundle
# from radcal.models import *
# import radprofile.resources
# from taxonomy.resources import *
from django.contrib.auth.models import Group
# #import copy
# from datetime import datetime, time, timedelta
# #import time
# import operator

class ProfileResource(ModelResource):
  class Meta:
    queryset = Profile.objects.all()
    fields = ['grad_year', 'short_range', 'phone']
    authentication = Authentication()
    authorization = DjangoAuthorization()
    validation = Validation()
    limit = 1000

class UserResource(ModelResource):
  profile = fields.ForeignKey(ProfileResource, 'profile', null=True)
  # profile = fields.ForeignKey(ProfileResource, 'profile', null=True)

  class Meta:
    queryset = User.objects.all().select_related('profile')
    excludes = ['password', 'email']
    authentication = Authentication()
    authorization = DjangoAuthorization()
    validation = Validation()
    limit = 1000

    filtering = {
      'username': ALL,
      }

class GroupResource(ModelResource):
  class Meta:
    queryset = Group.objects.all()
    excludes = []
    limit = 1000

    #    filtering = {
    #    }