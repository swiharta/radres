import datetime
from itertools import groupby
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.datastructures import SortedDict

def make_custom_datefield(f):
    formfield = f.formfield()
    if isinstance(f, models.DateField):
        formfield.widget.format = '%m/%d/%Y'
        formfield.widget.attrs.update({'class':'datePicker', 'readonly':'true'})
    return formfield

def get_send_mail():
  """
  A function to return a send_mail function suitable for use in the app. It
  deals with incompatibilities between signatures.
  """
  # favour django-mailer but fall back to django.core.mail
  if "mailer" in settings.INSTALLED_APPS:
    from mailer import send_mail
  else:
    from django.core.mail import send_mail as _send_mail
    def send_mail(*args, **kwargs):
      del kwargs["priority"]
      return _send_mail(*args, **kwargs)
  return send_mail

def get_initial_json(resource, **kwargs):
  resource_list = resource.get_object_list(None).filter(**kwargs)
  resource_to_serialize = [resource.full_dehydrate(resource.build_bundle(obj=obj)).data for obj in resource_list]
  resource_json = resource.serialize(None, resource_to_serialize, 'application/json')
  return resource_json

def get_initial_json_data(resource, **kwargs):
  resource_list = resource.get_object_list(None).filter(**kwargs)
  resource_to_serialize = [resource.full_dehydrate(resource.build_bundle(obj=obj)).data for obj in resource_list]
  return resource_to_serialize

def date_to_timezone(date_obj, time_obj = datetime.time.min):
  return timezone.make_aware(datetime.datetime.combine(date_obj, time_obj), timezone.get_default_timezone())

def group_by_date(events):
  if len(events):
    if hasattr(events[0], 'start'):
      field = lambda event: event.start.date()
    else:
      field = lambda event: event.date
    return dict( # keeps dates (keys) in order in the template for loop
        [(date, list(items)) for date, items in groupby(events, field)]
    )

def group_by_date_sorted(events):
  if len(events):
    if hasattr(events[0], 'start'):
      field = lambda event: event.start.date()
    else:
      field = lambda event: event.date
    return SortedDict( # keeps dates (keys) in order in the template for loop
        [(date, list(items)) for date, items in groupby(events, field)]
    )

def daterange(start_date, end_date):
    for n in range((end_date - start_date).days):
        yield start_date + timedelta(n)