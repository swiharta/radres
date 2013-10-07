from django.contrib.auth.models import User
from models import ShiftEvent
from datetime import date, datetime, timedelta
from django.core.cache import cache
from django.db.models import Q
import os.path, time
from django.utils.timezone import get_default_timezone
from django.conf import settings

def get_last_update_time():
  updated = cache.get('updated')
  if not updated:
#    updated = ShiftEvent.objects.all().order_by('-modified')[0].modified
    call_path = os.path.join(settings.PROJECT_ROOT, os.pardir, 'call.txt')
    if os.path.exists(call_path):
      updated = datetime.fromtimestamp(os.path.getmtime(call_path), get_default_timezone())
      cache.set('updated', updated, 3600)
    else:
      return None
  return updated

def get_user_event_ids(user):
  user_event_ids = cache.get('user_event_ids' + str(user.id), 'no_cache')
  if user_event_ids == 'no_cache':
    # print 'no user_event_ids'
    user_event_ids = ShiftEvent.objects.filter(user=user).values_list('id', flat=True)
    cache.set('user_event_ids' + str(user.id), user_event_ids, 43200)
  return user_event_ids

def get_upcoming_ids(user, user_events, start, horizon):
    upcoming_ids = cache.get('upcoming_ids' + str(user), 'no_cache')
#    upcoming_ids = None
    if upcoming_ids == 'no_cache':
      upcoming_ids = user_events.filter(date__gte=start,date__lte=horizon).values_list('id', flat=True)
      if not upcoming_ids: # get next soonest call after horizon date
        horizon_events = user_events.filter(date__gt=horizon).order_by('date')
        upcoming_ids = horizon_events.values_list('id', flat=True)[:1]
      cache.set('upcoming_ids' + str(user), upcoming_ids, 43200)
    return upcoming_ids

def get_user_conflict_ids(user, force_refresh=False):
  user_conflict_ids = cache.get('user_conflict_ids' + str(user.id), 'no_cache')
  if user_conflict_ids == 'no_cache' or force_refresh:
    hindsight = date.today() - timedelta(days = 14)
    events = ShiftEvent.objects.filter(user=user, date__gte=hindsight).order_by('date').select_related('shift__night_call')
    seen = set()
    conflict_dates = set()
    last_night_call = None
    for event in events:
      if event.date in seen:
        conflict_dates.add(event.date)
      else:
        seen.add(event.date)
      if (event.date - timedelta(days=1)) == last_night_call:
        conflict_dates.add(event.date)
        conflict_dates.add(last_night_call)
      if event.shift.night_call:
        last_night_call = event.date
    user_conflict_ids = ShiftEvent.objects.filter(user=user, date__in=conflict_dates).values_list('id', flat=True)
    cache.set('user_conflict_ids' + str(user.id), user_conflict_ids, 43200)
  return user_conflict_ids

def get_conflict_ids(force_refresh=False):
  conflict_ids = cache.get('conflict_ids', 'no_cache') #return an iterable if no conflicts

#  print 'cached conflict_ids: ' + str(conflict_ids)
#  conflict_ids = None

  if conflict_ids == 'no_cache' or force_refresh:
    conflict_ids = set()
#    dummy = get_dummy_user()
    for user in User.objects.all():
#      if not user == dummy:
        conflict_ids |= set(get_user_conflict_ids(user, force_refresh=force_refresh))
    cache.set('conflict_ids', conflict_ids, 43200) # 60s x 60min x 24h = 86400s

    print 'generated conflict_ids: ' + str(conflict_ids)

  return conflict_ids

def get_post_call_ids():
  post_call_ids = cache.get('post_call_ids', [])
  if not post_call_ids:
    hindsight = date.today() - timedelta(days = 90)
    post_call_ids = ShiftEvent.objects.filter(Q(shift__initials="Mt") | Q(shift__night_call=True),
                                           date__gte=hindsight, date__lte=date.today()).values_list('id', flat=True)
    cache.set('post_call_ids', post_call_ids, 43200)

#def get_dummy_user():
#  dummy = cache.get('dummy_user')
#  if not dummy:
#    dummy = User.objects.get(id=16)
#    cache.set('dummy_user', dummy, 2592000)
#  return dummy