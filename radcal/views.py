from datetime import date, timedelta, datetime
from dateutil.relativedelta import relativedelta
# from itertools import chain
# from operator import attrgetter
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required#, permission_required
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse#, Http404,
from django.shortcuts import get_object_or_404#, render_to_response
from django.views.generic.list_detail import object_list, object_detail
from django.views.generic.simple import direct_to_template
from django.utils.safestring import mark_safe
from django.utils import simplejson
from django.utils.datastructures import SortedDict
from radres.utils import get_initial_json, date_to_timezone, daterange, group_by_date_sorted#, group_by_date
import radprofile.resources, taxonomy.resources
from radprofile.forms import UserSelect#, ProfileForm
from .forms import *
from .resources import *
from .calendars import UserCalendar, CallCalendar
from .utils import *

from raven.contrib.django.raven_compat.models import client
client.captureException()

def home(request):
  today = date.today()# + timedelta(days = 1)
  tomorrow = today + timedelta(days = 1)
  today_weekday = today.weekday() # sunday = 6, monday = 0
  sunday = date_to_timezone(today - timedelta(days = today_weekday+1))
  saturday = date_to_timezone(today + timedelta(days = 5-today_weekday))
  if today_weekday > 4: # if weekend, show conferences for next week
    sunday = sunday + timedelta(days = 7)
    saturday = saturday + timedelta(days = 7)
  next_sunday = sunday + timedelta(days = 7)
  prev_sunday = sunday - timedelta(days = 7)
  conf_week = cache.get('conf_week')
  if not conf_week:
    conf_week = ConfEvent.objects.filter(start__gte=sunday, start__lte=saturday).order_by('start')
    cache.set('conf_week', conf_week, 4800)
  if conf_week:
    conf_days = group_by_date_sorted(conf_week)
  else:
    conf_days = []

  if request.GET.get('new_month'):
    month_string = request.GET.get('new_month')
    month = int(month_string.split(' ')[0])
    year = int(month_string.split(' ')[1])
    print month, year
    first = date(year, month, 1)
  else:
    first = date(today.year, today.month, 1)
    year = date.today().year
    month = date.today().month

  next_first = first + relativedelta(months=+1)
  horizon = today + timedelta(days = 7)
  updated = get_last_update_time()

  if request.user.is_authenticated():
    user_events = ShiftEvent.objects.filter(user=request.user)
    cal_events = user_events.filter(date__gte=first,date__lt=next_first).order_by('date').select_related()
    upcoming_ids = get_upcoming_ids(request.user, user_events, today, horizon)
    user_conflict_ids = get_user_conflict_ids(request.user)

    user_agenda_ids = set(upcoming_ids) | set(user_conflict_ids)
    agenda = ShiftEvent.objects.filter(id__in=user_agenda_ids).order_by('date').select_related()

    htmlcal = UserCalendar(cal_events)
    htmlcal.setfirstweekday(6) # 6 = Sunday
    cal = htmlcal.formatmonth(year, month)

# ---Below combines this week's conf_events and user shift_events into `conferences`---
#    agenda_qsets = sorted(chain(conf_week, user_agenda),key=attrgetter('date'))=
#    conference_days = group_by_date(conf_week) # takes a QuerySet or sorted, chained QuerySets, as above
#    conferences = []
#    week_list = [ sunday + timedelta(days=x) for x in range(0,7) ]
#    for weekday in week_list:
#      day = {'date': weekday, 'classes': weekday.strftime('%a ')}
#      if not weekday == today:
#        day['classes'] += 'inactive '
#      else:
#        day['classes'] += 'active today '
#      if weekday in conference_days:
#        events = []
#        for event in conference_days[weekday]:
#          event.classes = event.get_classes()
#          events.append(event)
#        day['events'] = events
#      else:
#        day['classes'] += 'empty '
#        day['events'] = []
#      conferences.append(day)

  else:
    agenda = cal = user_conflict_ids = user_events = [1,2] # some stupid bug, these vars need to be iterables

  if request.GET.get('new_month') and request.is_ajax(): # returns new month html fragment for agenda calendar
    return direct_to_template(request, 'radcal/calendar.html', extra_context =
            {'calendar':mark_safe(cal)})

  if request.is_ajax():
    return HttpResponse(simplejson.dumps({'location': '/'}), mimetype="application/json")

  return direct_to_template(request, 'radres.html', extra_context =
            {'agenda': agenda, 'today': today, 'tomorrow': tomorrow,#'start': sunday, 'end': saturday,
             'calendar': mark_safe(cal), 'conferences': conf_days,#'old_agenda': agenda,
             'prev_sunday': prev_sunday, 'next_sunday': next_sunday,
             'conflicts': user_conflict_ids, 'updated': updated,
             'no_user_events': bool(not user_events)})


def fullcal(request):
  c = ConferenceResource()
  ce = ConfEventResource()

  ce_json = cache.get('ce_json')
  if not ce_json:
    today = date.today()
    first = date(today.year, today.month, 1)
    first_prev = (first - relativedelta(months=4))
    first_next = (first + relativedelta(months=8))
    start = date_to_timezone(first_prev + relativedelta(days=22)) # 23rd is earliest day possibly displayed = leap year with 3/1 on Saturday
    end = date_to_timezone(first_next + relativedelta(days=12)) # 13th is latest day possibly displayed = last day of current month on Sunday

    ce_json = get_initial_json(ce, start__gte=start, start__lt=end)
    cache.set('ce_json', ce_json, 86400) # 60s x 60min x 24h = 86400s

  c_json = cache.get('c_json')
  if not c_json:
    c_json = get_initial_json(c)
    cache.set('c_json', c_json, 2592000) # i think this is the maximum possible

  divs = SortedDict(DIV_CHOICES)

  return direct_to_template(request, 'radcal/fullcal.html', extra_context = {
             'ce_json': ce_json,
             'c_json': c_json,
             'divs': divs,
             }
  )

def call(request):
  ef = EventFilterResource()
  se = ShiftEventResource()
  ce = ConfEventResource()
  s = ShiftResource()
  c = ConferenceResource()
  u = radprofile.resources.UserResource()

  sub = taxonomy.resources.SubspecialtyResource()

  for key, resource in [('se_json', se), ('ce_json', ce)]:
    if not cache.get(key):
      today = date.today()
      first = date(today.year, today.month, 1)
      first_prev = (first - relativedelta(months=1))
      first_next = (first + relativedelta(months=2))
      start = date_to_timezone(first_prev + relativedelta(days=22)) # 23rd is earliest day possibly displayed = leap year with 3/1 on Saturday
      end = date_to_timezone(first_next + relativedelta(days=12)) # 13th is latest day possibly displayed = last day of current month on Sunday

      json = get_initial_json(resource, start__gte=start, start__lt=end)
      cache.set(key, json, 43200) # 60s x 60min x 24h = 86400s
  #
  for key, resource in [('s_json', s), ('c_json', c), ('sub_json', sub)]: #('u_json', u)
    if not cache.get(key):
      json = get_initial_json(resource)
      cache.set(key, json, 2592000) # i think this is the maximum possible

  if not cache.get('u_json'):
    u_json = get_initial_json(u)
    cache.set('u_json', u_json, 2592000) # i think this is the maximum possible
  #
  for key, resource in [('ef_json', ef)]:
    json = get_initial_json(resource)
    cache.set(key, json, 2592000) # i think this is the maximum possible

  return direct_to_template(request, 'radcal/call.html', extra_context = {
               'se_json': cache.get('se_json'),
               'ce_json': cache.get('ce_json'),
               's_json': cache.get('s_json'),
               'c_json': cache.get('c_json'),
               'u_json': cache.get('u_json'),
               'sub_json': cache.get('sub_json'),
               'ef_json': cache.get('ef_json'),
               'divs': SortedDict(DIV_CHOICES)
               }
  )

def shift_table(request):
  today = date.today()
  end = today + timedelta(weeks=10)
  days = daterange(today, end)
  day_events = group_by_date_sorted(ShiftEvent.objects.filter(date__gte=today,
                                 date__lte=end).order_by('date').select_related())
  shifts = Shift.objects.all()
  return object_list(request, queryset=ShiftEvent.objects.all().select_related(),
                     template_name="radcal/shift_table.html",
#                     template_object_name="event",
                     extra_context={'day_events': day_events, "shifts": shifts, 'days': days})# shift_formset})

def shift_event(request, event_id):
  if request.method == 'GET':
    return object_detail(request,queryset=ShiftEvent.objects.filter(id=event_id).select_related(),
              object_id=event_id, template_name='radcal/shift_event.html',
              template_object_name = 'event')#, extra_context = {'shift_form':shift_form})
  if request.method == 'POST':
    event1 = ShiftEvent.objects.get(id=event_id)
    form = ShiftForm(data=request.POST)#, instance=event)
    if form.is_valid():
      event2 = get_object_or_404(ShiftEvent, **form.cleaned_data)
#      event2 = form.save(commit=False)
      event1.resident, event2.resident = event2.resident, event1.resident
      event1.user, event2.user = event2.user, event1.user
      event1.save()
      event2.save()
    else:
      print 'failed'
    return HttpResponseRedirect(reverse("cal_index"))

def conferences(request): # returns html fragments for navigating weekly conferences
  today = date.today()
  if request.GET.get('sunday'):
    sunday_string = request.GET.get('sunday')
    sunday = datetime.strptime(sunday_string, '%m-%d-%y')
    saturday = sunday + timedelta(days=6)
    next_sunday = sunday + timedelta(days = 7)
    prev_sunday = sunday - timedelta(days = 7)
    conf_week = ConfEvent.objects.filter(start__gte=sunday, start__lte=saturday).order_by('start')
    conf_days = group_by_date_sorted(conf_week)
  else:
    prev_sunday = next_sunday = conf_days = [1,2]
  return direct_to_template(request, 'radcal/conf_week.html', extra_context =
    {'conferences':conf_days, 'prev_sunday': prev_sunday,
     'next_sunday': next_sunday, 'today': today})

def cal_index(request, template_name='radcal/cal_index.html', *args, **kwargs):
  filters = cal_filters(request)
  switches = cal_switches(request)
  residents = cal_residents(request)
  qsets = cal_shiftevents(request)
  if request.method == 'GET':
#    data = {
#      'form-TOTAL_FORMS': u'2',
#      'form-INITIAL_FORMS': u'2',
#      'form-MAX_NUM_FORMS': u'',
#    }
    shift_formset = ShiftFormset()#(initial=[{'user': user}])
#    conf_formset = ConfFormset()

    if request.GET.get('new_month'):
      month_string = request.GET.get('new_month')
      month = int(month_string.split(' ')[0])
      year = int(month_string.split(' ')[1])
      first = date(year, month, 1)
    else:
      first = None
      year = date.today().year
      month = date.today().month

    shifts = shift_set(request, qsets, filters, switches, residents, first=first)
    htmlcal = CallCalendar(shifts, request.user, residents)
    htmlcal.setfirstweekday(6) # 6 = Sunday
    cal = htmlcal.formatmonth(year, month)
    user_select = UserSelect(initial={'users': residents})

    conflict_switch_status = bool(switches)

    if request.is_ajax() and request.GET.get('new_month'):
      return direct_to_template(request, 'radcal/calendar.html', extra_context =
            {'calendar':mark_safe(cal), 'filters': filters})
    else:
      filter_form = FilterForm(initial=filters)

      return direct_to_template(request, template_name, extra_context =
            {'shift_formset': shift_formset,# 'conf_formset': conf_formset,
             'calendar':mark_safe(cal), 'filters': filters, 'filter_form': filter_form,
             'user_select': user_select, 'conflict_switch': conflict_switch_status })

  if request.method == "POST":
    shift_formset = ShiftFormset(data=request.POST)
    if shift_formset.is_valid():
      mod_events = []
      mods = [request.user] # start building moderators list
      # [{'date':e.date, 'user':e.user, 'shift':e.shift} for e in events]
      for form in shift_formset:
#        if not form in shift_formset.deleted_forms:
        event = get_object_or_404(ShiftEvent, shift=form.cleaned_data['shift'],
                                  date=form.cleaned_data['date'])
#        event = form.save(commit=False)
        mods.append(event.user)
        event.user = form.cleaned_data['user']
        event.save()
        mod_events.append(event)
        mods.append(event.user)
      mods = set(mods)
      for event in mod_events:
        event.moderated_object.approved_by = [request.user]
        event.moderated_object.moderators = mods
        event.moderated_object.save()
      print 'success'
    else:
      print "sucks to be you"

    return HttpResponseRedirect(reverse('cal_index'))


def cal_switches(request):
  switches = {}
  if request.method == 'GET':
    for field in SwitchForm():
      if request.session.get(field.name):
        switches[field.name] = request.session.get(field.name)
    return switches
  if request.method == 'POST':
    switch_form = SwitchForm(data=request.POST)
    if switch_form.is_valid(): # auto-converts javascript 'false' to False / 'true' to True
      for field in switch_form:
        request.session[field.name] = switch_form.cleaned_data[field.name]
      switches = switch_form.cleaned_data
    else:
      if request.is_ajax():
        return HttpResponse(u'failure')
    if request.is_ajax():
      return HttpResponse(simplejson.dumps(switches), mimetype="application/json")
    else:
      return HttpResponseRedirect(reverse("cal_index"))


def cal_filters(request):
  filters = {}
  if request.method == 'GET':
    for field in FilterForm():
      if request.session.get(field.name):
        filters[field.name] = request.session.get(field.name)
    return filters
  if request.method == 'POST':
    filter_form = FilterForm(data=request.POST)
    if filter_form.is_valid(): # auto-converts javascript 'false' to False / 'true' to True
      for field in filter_form:
        request.session[field.name] = filter_form.cleaned_data[field.name]
      filters = filter_form.cleaned_data
    else:
      if request.is_ajax():
        return HttpResponse(u'failure')
    if request.is_ajax():
      return HttpResponse(simplejson.dumps(filters), mimetype="application/json")
    else:
      return HttpResponseRedirect(reverse("cal_index"))


def cal_residents(request):
  residents = {}
  if request.method == 'GET':
    residents = request.session.get('residents')
    if request.is_ajax():
      return residents
    else:
      if not residents:
        request.session['residents'] = [request.user.id]
        return [request.user.id]
      if not request.user.id in residents:
        residents.append(request.user.id)
      request.session['residents'] = residents
      return residents
  if request.method == 'POST':
    user_form = UserSelect(data=request.POST)
    if user_form.is_valid(): # converted javascript 'false' to False / 'true' to True (?)
      request.session['residents'] = user_form.cleaned_data['users']
      residents = user_form.cleaned_data
    else:
      if request.is_ajax():
        return HttpResponse(u'failure')
    if request.is_ajax():
      return HttpResponse(simplejson.dumps(residents), mimetype="application/json")
    else:
      return HttpResponseRedirect(reverse("cal_index"))


@login_required
def cal_shiftevents(request):
  qsets = {}

  EVENT_CACHE_KEYS = {
#    'user_events': ShiftEvent.objects.filter(user=request.user).values_list('id', flat=True),
    'night_call_events': ShiftEvent.objects.filter(shift__night_call=True).values_list('id', flat=True),
    'day_call_events': ShiftEvent.objects.filter(shift__day_call=True).values_list('id', flat=True),
    'ED_events': ShiftEvent.objects.filter(shift__abbr__startswith="ED").values_list('id', flat=True),
    'IR_events': ShiftEvent.objects.filter(shift__abbr="Angio").values_list('id', flat=True),
    'moon_events': ShiftEvent.objects.filter(shift__cash__isnull=False).values_list('id', flat=True),
    'mod_events': [],#ModeratedObject.objects.filter(moderation_status=MODERATION_STATUS_PENDING).values_list('id', flat=True).values_list('id', flat=True)
  }

#  for res in User.objects.all():
#    EVENT_CACHE_KEYS[res.username+'_events'] = ShiftEvent.objects.filter(shift__overnight=True)\
#                                               .values_list('id', flat=True)

  for key, value in EVENT_CACHE_KEYS.items():
    qsets[key] = cache.get(key)

    if not qsets[key]:
      cache.set(key, value, 21600) # store (TODO: monthly) caches with 40 minute expiration
      qsets[key] = cache.get(key)
#       qsets[key] = value # for ignoring the cache

#  for qset, values in qsets.items():
#    print '%s: %s' % (qset, values)
  return qsets


def shift_set(request, qsets, filters, switches, residents, first=None):
#  return ShiftEvent.objects.filter(user=request.user)
  qsets = qsets
  filters = filters
  switches = switches
  residents = residents
#  print 'conflict_switch: ', conflict_switch

  today = date.today()
  if not first:
    first = date(today.year, today.month, 1)
  first_next = first + relativedelta(months=+1)
  qids = ShiftEvent.objects.none()

  if residents:
    qids = ShiftEvent.objects.filter(user__in=residents).values_list('id', flat=True)
  else:
    pass
  if filters:
    for name, value in filters.items():
      if not value: # don't include False filters in lookups
        del filters[name]
      else:
        # | creates the union of two QuerySets (Django feature, not straight Python)
        qids = qids | qsets[name.replace('_filter', '_events')]
#        qids = qids | qsets[filter.replace('_filter', '_events') + first.strftime('%m-%Y')]
#        qids = chain(qids, qsets[filter.replace('_filter', '_events')])

  qids = ShiftEvent.objects.filter(date__gte=first, date__lt=first_next, id__in=qids).values_list('id', flat=True)
  print switches
  if switches:
    for switch, value in switches.items():
      print '%s: %s' % (switch, value)
      if not value:
        del switches[switch]
      else:
        conflict_ids = get_conflict_ids()
        conflict_qids = ShiftEvent.objects.filter(date__gte=first, date__lt=first_next, id__in=conflict_ids).values_list('id', flat=True)
        qids = set(qids) | set(conflict_qids)
#  qset = ShiftEvent.objects.filter(id__in=qids).order_by('start', 'end').select_related()
  qset = ShiftEvent.objects.filter(id__in=qids).order_by('date', 'shift').select_related()
  return qset


from django_cal.views import Events

class UserEvents(Events):
    def get_object(self, request, username):
        return User.objects.get(username=username)
    
    def items(self, obj):
        if obj.get_profile().ical:
          return ShiftEvent.objects.filter(user=obj)
        else:
          return []

    def cal_name(self, obj):
#        return obj.get_profile().get_full_name()
        return 'RadRes (' + obj.get_profile().get_full_name() + ')'

    def cal_desc(self, obj):
#        return obj.get_profile().get_full_name()
        return "RadRes.Info call and moonlighting schedule for " + obj.get_profile().get_full_name()

    def item_summary(self, item):
        return item.shift.name

    def item_start(self, item):
        return item.date

    def item_end(self, item):
        return item.date
