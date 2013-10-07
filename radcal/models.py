from django.db import models
from django.utils.translation import ugettext, ugettext_lazy as _
from django.contrib.auth.models import Group
from django.utils.timezone import is_aware
from datetime import date, timedelta, datetime
from django.contrib.auth.models import User
from django.utils.timezone import is_aware, localtime
from templatetags.my_tags import humanize_timeuntil, humanize_timesince
from taxonomy.models import Subspecialty
#from radcal.utils import *
# import django_monitor

class EventType(models.Model):
  name = models.CharField(_('name'), max_length=30)
  abbr = models.CharField(_('name abbreviation'), max_length=20, null=True, blank=True)
  start_time = models.TimeField(_('start time'), null=True, blank=True)
  end_time = models.TimeField(_('end time'), null=True, blank=True)
#  days = models.CharField(_('days'), max_length=8, default="PUH", choices=DAYS)
  class Meta:
    abstract = True

HOSPITALS = (
  ("SHY", "Shadyside"),
  ("PUH", "Presby / Monte"),
  ("MER", "Mercy"),
  ("MWH", "Magee"),
  ("MVL", "Monroeville"),
  ("HIL", "Hillman"),
  ("SMED", "Sports"),
  ("CHP", "Children's")
  )

class Shift(EventType):
  code = models.CharField(_('shift codename'), max_length=20, null=True, blank=True)
  initials = models.CharField(_('shift initials'), max_length=8, null=True, blank=True)
  description = models.TextField(_('shift description'), null=True, blank=True)
  hospital = models.CharField(_('hospital'), max_length=8, default="PUH", choices=HOSPITALS)
  cash = models.IntegerField(_('cash'), null=True, blank=True)
  hourly_cash = models.IntegerField(_('hourly cash'), null=True, blank=True)
  day_call = models.BooleanField(default=False)
  night_call = models.BooleanField(default=False)
  weekend = models.BooleanField(default=False)

  def __unicode__(self):
    return self.name

class Conference(EventType):
  location = models.CharField(_('conference location'), max_length=30, null=True, blank=True)

  def __unicode__(self):
    return '%s' % self.name

class EventFilter(models.Model):
  owner = models.ForeignKey(User, related_name="%(class)s_owners", default=16)
  group = models.ForeignKey(Group, related_name="%(class)ss", null=True, blank=True)
  default = models.BooleanField(default=False) # default = user's last EventFilter

  name = models.CharField(_('name'), max_length=30)
  abbr = models.CharField(_('name abbreviation'), max_length=20, blank=True)

  shifts = models.ManyToManyField(Shift, null=True, blank=True)
  users = models.ManyToManyField(User, related_name="%(class)ss", null=True, blank=True)
  conferences = models.ManyToManyField(Conference, null=True, blank=True)
  subspecialties = models.ManyToManyField(Subspecialty, null=True, blank=True, related_name="eventfilter_subspecialties")

  def __unicode__(self):
    return '%s' % self.name

class EventManager(models.Manager):
  def get_public(self):
    return self.get_query_set().filter(public=True)


class Event(models.Model):
  created = models.DateTimeField(_('created'), auto_now_add=True)
  modified = models.DateTimeField(_('modified'), auto_now=True)
  public = models.BooleanField(default=True)
  remind = models.BooleanField(default=False)
  date = models.DateField(_('date'))
  start = models.DateTimeField(_('event start'), null=True, blank=True, help_text='Select "Conference type", and only enter a start time if different than usual!') # for overriding conf.start
  end = models.DateTimeField(_('event end'), null=True, blank=True, help_text='Select "Conference type", and only enter an end time if different than usual!') # for overriding conf.end

  objects = EventManager()

  class Meta:
    abstract = True


class ShiftTrade(models.Model):
  creator = models.ForeignKey(User, related_name="%(class)ss")
  message = models.CharField(_('message'), max_length=200, blank=True)

class ShiftEvent(Event):
  user = models.ForeignKey(User, related_name="%(class)ss", blank=True, null=True, on_delete=models.SET_NULL)
  resident = models.CharField(_('resident'), max_length=50, blank=True)
  shift = models.ForeignKey(Shift)
  trade = models.ForeignKey(ShiftTrade, blank=True, null=True)
  visible = models.BooleanField(default=True)
  pending = models.BooleanField(default=False)

  def __unicode__(self):
    return str(self.date) + " - " + self.date.strftime('%a') + " - "\
           + self.shift.name + " - " + self.resident

  def get_absolute_url(self):
    return "/calendar/shifts/event/%i/" % self.id

  def get_classes(self):
  #    if self.id in get_user_conflict_ids(user):
  #      self.classes += 'conflict '
  #      self.conflict = True
  #    if self.user == user:
  #      self.classes += 'you '
    self.classes = 'shift '
    if self.shift.cash:
      self.classes += 'moon '
    elif self.shift.abbr[:2] == "ED":
      self.classes += 'ED '
    elif self.shift.abbr == "Angio":
      self.classes += 'IR '
    elif self.shift.day_call:
      self.classes += 'day '
    self.classes += self.get_state()
    return self.classes

  def get_state(self):
    today = date.today()# + timedelta(days = 4)
    horizon = today + timedelta(days = 7)
    self.state = ''
    #    print self.date, today
    if self.date < today or self.date > horizon:
      self.state = 'inactive '
    if self.date < today:
      self.state += 'past '
    if self.date == today:
      self.state = 'active '
    #    if self.date == today + timedelta(days = 1):
    #      self.state += 'semiactive '
    print self.state
    return self.state

  def get_time_relative(self):
    today = date.today()# + timedelta(days = 4)
    self.time_relative = 'in ' + humanize_timeuntil(self.date)
    if self.date == today + timedelta(days = 1):
      self.time_relative = 'tomorrow'
    if self.date == today:
      self.time_relative = 'today'
    if self.date < today:
      self.time_relative = humanize_timesince(self.date)
    return self.time_relative


#django_monitor.nq(ShiftEvent)
#class ShiftEventChange(ShiftEvent)

CONF_TYPE_CHOICES = (
  ('noon', 'Noon Conference'),
  ('7am', '7am Conference'),
  ('am', 'Morning Conference'),
  ('other', 'Other Conference'),
)

DIV_CHOICES = (
  ('Cardiac', 'Cardiac Imaging'),
  ('Chest', 'Chest Imaging'),
  ('ED', 'Emergency Radiology'),
  ('ENT', 'Head and Neck'),
  ('GI', 'Gastrointestinal'),
  ('Grand', 'Grand Rounds'),
  ('GU', 'Genitourinary'),
  ('Mammo', 'Mammography'),
  ('MSK', 'Musculoskeletal'),
  ('Neuro', 'Neuroradiology'),
  ('Nucs', 'Nuclear Medicine'),
  ('Peds', 'Pediatric Imaging'),
  ('Physics', 'Radiology Physics'),
  ('IR', 'Vascular / Interventional'),
  ('WI', 'Women\'s Imaging'),
)

class ConfEvent(Event):
  div = models.CharField(_('subdivision'), max_length=20, choices=DIV_CHOICES, blank=True)
  subspecialty = models.ForeignKey(Subspecialty, null=True, blank=True, related_name="confevent_subspecialty")
  title = models.CharField(_('title'), max_length=200, blank=True)
  link = models.URLField(_('7pumps link'), blank=True)
  #  user = models.ForeignKey(User, related_name="owned_%(class)ss")
  presenter = models.CharField(_('presenter(s)'), max_length=100, blank=True)
  venue = models.CharField(_('conference venue'), max_length=8, default="noon", choices=CONF_TYPE_CHOICES)
  conference = models.ForeignKey(Conference, verbose_name=_('conference type'), null=True, blank=True)

  def __unicode__(self):
    return '%s - %s' % (self.div, self.title)

  def get_classes(self): # user unused for now, but matches with ShiftEvent method calls
    today = date.today()# + timedelta(days = 4)
    if not self.date == today:
      self.classes = 'inactive '
    else:
      self.classes = 'active '
    return self.classes

  def get_short_time(self): # for generating '12p', '7:06a' formats
    start = localtime(self.start)
    AMPM = datetime.strftime(start, '%p').rstrip('M').lower()
    mins = datetime.strftime(start, '%M')
    if not int(mins):
      mins = ''
    else:
      mins = ':' + str(mins)
    hour = datetime.strftime(start, '%I').lstrip('0')
    short_time = hour + mins + AMPM
    return short_time

#  def save(self, *args, **kwargs):
#    if self.conf:
##      self.start = self.conf.start
##      self.end = self.conf.end
#    else:
#      super(ConfEvent, self).save(*args, **kwargs) # Call the "real" save() method.
