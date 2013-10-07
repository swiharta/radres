import operator
from datetime import timedelta # datetime, time
# import copy
# import time
from django.db.models import Q
from tastypie.authentication import BasicAuthentication, Authentication
from tastypie.authorization import DjangoAuthorization, Authorization
from tastypie.validation import Validation
from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from tastypie import fields
# from tastypie.cache import SimpleCache
# from tastypie.bundle import Bundle
import radprofile.resources
import taxonomy.resources
from .models import *

class ShiftResource(ModelResource):
  class Meta:
    queryset = Shift.objects.all()

    filtering = {
      'abbr': ALL,
      'name': ALL,
      'cash': ALL,
      'day_call': ALL,
      'night_call': ALL
    }

class ConferenceResource(ModelResource):
  class Meta:
    queryset = Conference.objects.all()
    authentication = Authentication()
    authorization = DjangoAuthorization()
    validation = Validation()

  def obj_update(self, bundle, request=None, **kwargs):
    bundle = super(ConferenceResource, self).obj_update(bundle, **kwargs)
    for field_name in self.fields:
      print field_name
      field = self.fields[field_name]
      if type(field) is fields.ToOneField and field.null == True and bundle.data[field_name] == None:
        setattr(bundle.obj, field_name, None)
        bundle.obj.save()
    return bundle

class EventFilterResource(ModelResource):
  owner = fields.ForeignKey(radprofile.resources.UserResource, 'owner')
  group = fields.ForeignKey(radprofile.resources.GroupResource, 'group', null=True)

  shifts = fields.ToManyField(ShiftResource, 'shifts', null=True) # these generate an SQL query for each object
  users = fields.ToManyField(radprofile.resources.UserResource, 'users', null=True)
  subspecialties = fields.ToManyField(taxonomy.resources.SubspecialtyResource, 'subspecialties', null=True) # these generate an SQL query for each object
  conferences = fields.ToManyField(ConferenceResource, 'conferences', null=True)

  class Meta:
    queryset = EventFilter.objects.all().select_related('shifts','users','conferences','subspecialties','owner','group')
    authentication = Authentication()
    authorization = DjangoAuthorization()
    validation = Validation()

    filtering = {
      'shifts': ALL,
      'users': ALL,
      'conferences': ALL,
      'subspecialties': ALL,
      'owner': ALL,
      'group': ALL,
      'default': ALL
    }

class ShiftTradeResource(ModelResource):
  creator = fields.ForeignKey(radprofile.resources.UserResource, 'creator')

  class Meta:
    queryset = ShiftTrade.objects.all()

class ShiftEventResource(ModelResource):
  shift = fields.ForeignKey(ShiftResource, 'shift') # these generate an SQL query for each object
  user = fields.ForeignKey(radprofile.resources.UserResource, 'user', null=True)
#  trade = fields.ForeignKey(ShiftTradeResource, 'trade')

  class Meta:
    queryset = ShiftEvent.objects.all().select_related('shift','user')
    excludes = ['created', 'modified', 'pending', 'public', 'remind', 'visible']
    limit=50000
    max_limit=50000
    authentication = Authentication()
    authorization = DjangoAuthorization()
    validation = Validation()

    filtering = {
      'date': ALL,
      'start': ALL,
      'user': ALL_WITH_RELATIONS,
      'shift': ALL_WITH_RELATIONS,
    }

  def dehydrate(self, bundle):
#    bundle.data['className'] = 'shift'
#    bundle.data['color'] = '#6ACDC3'
#    bundle.data['textColor'] = '#444'
#    if bundle.data['shift'].data['cash']:
#      bundle.data['color'] = '#57C784'
#    elif bundle.data['shift'].data['day_call']:
#      bundle.data['color'] = '#e7ddd3'
#    elif bundle.data['shift'].data['abbr'] == "Angio":
#      bundle.data['color'] = '#D5B3D5'
#    elif bundle.data['shift'].data['abbr'][:2] == 'ED':
#      bundle.data['color'] = '#c88558'
#      bundle.data['textColor'] = '#fff'

    bundle.data['editable'] = False
    bundle.data['title'] = ''
#    bundle.data['start'] = bundle.data['date']# + 'T' + bundle.data['shift'].data['start']
##    bundle.data['title'] = '%s (%s)' % (bundle.data['resident'], bundle.data['shift'].data['initials'])
#    bundle.data['shift__initials'] = bundle.data['shift'].data['initials']
#    bundle.data['shift__name'] = bundle.data['shift'].data['name']
#    if bundle.data['shift'].data['cash']:
#      cash_string = '- $%s' % bundle.data['shift'].data['cash']
#    else:
#      cash_string = ''
#    bundle.data['shift__cash'] = cash_string
#    bundle.data['shift__name'] = bundle.data['shift'].data['name']
#    bundle.data['shift__start'] = bundle.data['shift'].data['start']
#    bundle.data['shift__end'] = bundle.data['shift'].data['end']
##    bundle.data['shift'] = bundle.data['shift']['name']
#    del(bundle.data['shift'])
#    del(bundle.data['resident'])
#    del(bundle.data['date'])
    corrected_end = bundle.data['end'] - timedelta(hours = 4)
    bundle.data['allDay'] = True
    if corrected_end.date() > bundle.data['date']:
      bundle.data['end'] = bundle.data['end'] - timedelta(days = 1)
#    else:
#      bundle.data['allDay'] = False
    return bundle

  def build_filters(self, filters=None):
    if filters is None:
      filters = {}

    orm_filters = super(ShiftEventResource, self).build_filters(filters)

#    # for plain JSON feed as event data for FullCalendar, rather than storing it all in a Backbone Collection
#    # next / prev buttons fire a request with 'start' and 'end' GET parameters
#    # convert 'start' and 'end' Unix timestamps to datetime objects
#    # http://arshaw.com/fullcalendar/docs/event_data/events_json_feed/
#    if "start" in filters:
#      start = datetime.datetime.fromtimestamp(int(filters['start']))
#      orm_filters["date__gte"] = start
#
#    if "end" in filters:
#      end = datetime.datetime.fromtimestamp(int(filters['end']))
#      orm_filters["date__lte"] = end

    if "users" in filters:
      user_ids = [int(user_id) for user_id in filters['users'].split(',')]
      orm_filters['user_id__in'] = user_ids
#       queryset = ShiftEvent.objects.filter(Q(user_id__in=user_id_list,
#                                              date__gte=orm_filters['date__gte'],
#                                              date__lt=orm_filters['date__lt'])
#                                              | Q(**orm_filters))
#       orm_filters = {"pk__in": queryset}#[ i.pk for i in queryset ]}

    return orm_filters

  def apply_filters(self, request, filters):
#    if "user_id__in" in filters:
#      user_filters = {k: filters[k] for k in ('user_id__in', 'date__gte', 'date__lt')}
    date_filters = {}
    q_objects = []
    for k, v in filters.items():
      if 'date' in k: # catches 'date__*'
        date_filters[k] = v
        del filters[k] # get rid of date filters
      else:
        q_objects.append(Q(**{k: v}))

    if filters:
      return self.get_object_list(request).filter(reduce(operator.or_, q_objects), Q(**date_filters))
    return self.get_object_list(request).filter(**date_filters)

         # for this crazy trick: http://reliablybroken.com/b/tag/django/page/2/
         # basically inserts a | between the q_objects


class ConfEventResource(ModelResource):
  subspecialty = fields.ForeignKey(taxonomy.resources.SubspecialtyResource, 'subspecialty', null=True)#, full=True)
  conference = fields.ForeignKey(ConferenceResource, 'conference', null=True)#, full=True)

  class Meta:
    queryset = ConfEvent.objects.all().select_related('conference', 'subspecialty')
    excludes = ['created', 'modified', 'public', 'remind']
#    include_resource_uri = False
    limit = 10000
    max_limit = 10000
#    cache=SimpleCache() #has very little effect if any
    authentication = Authentication()
    authorization = DjangoAuthorization()
    validation = Validation()

    filtering = {
      'date': ALL,
      'start': ALL,
      'division': ALL,
      'presenter': ALL,
      'conference': ALL_WITH_RELATIONS,
      'subspecialty': ALL,
      'link': ALL,
#      'venue': ALL,
      }


  def dehydrate(self, bundle):
#    bundle.data['title'] = bundle.data['title']
#    bundle.data['textColor'] = '#444'
#    bundle.data['color'] = '#fff'#'#e7ddd3'
#    print time.mktime(bundle.data['date'].timetuple()) # = Unix timestamp
    bundle.data['allDay'] = False
#    del bundle.data['date']
    return bundle

  def build_filters(self, filters=None):
    if filters is None: # needed?
      filters = {}

    orm_filters = super(ConfEventResource, self).build_filters(filters)

    if "gap" in filters:
      orm_filters['gap'] = filters['gap']
    return orm_filters

  def apply_filters(self, request, filters):
  #    if "user_id__in" in filters:
  #      user_filters = {k: filters[k] for k in ('user_id__in', 'date__gte', 'date__lt')}
    req_filters = {}
    q_objects = []
    if 'gap' in filters:
      del filters['gap'] # this is just a flag to signal we want to OR the date parameters
      or_filters = True
      for k, v in filters.items():
#        if 'date' in k: # catches 'date__*'
#          req_filters[k] = v
#          del filters[k] # get rid of date filters
#        else:
        q_objects.append(Q(**{k: v}))
      return self.get_object_list(request).filter(reduce(operator.or_, q_objects), Q(**req_filters))
    else:
      req_filters = filters
      return self.get_object_list(request).filter(**req_filters)