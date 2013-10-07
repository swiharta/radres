# from django.contrib.auth.models import User
# from django.db.models import Q
from tastypie.authentication import Authentication#, BasicAuthentication
from tastypie.authorization import DjangoAuthorization#, Authorization
from tastypie.validation import Validation
from tastypie.resources import ModelResource, Resource, ALL, ALL_WITH_RELATIONS
from tastypie import fields

from .models import *

class SubspecialtyResource(ModelResource):
  class Meta:
    queryset = Subspecialty.objects.all()
    authentication = Authentication()
    authorization = DjangoAuthorization()
    validation = Validation()
    limit = 1000

    filtering = {
      'name': ALL,
      'abbr': ALL,
      }