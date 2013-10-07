# http://djangosnippets.org/snippets/2275/
import datetime

from django import template
from django.utils.translation import ugettext, ungettext
from django.utils.timezone import get_default_timezone

register = template.Library()


@register.filter(name='timesince_human')
def humanize_timesince(date):
    if isinstance(date, datetime.datetime):
      tz = get_default_timezone()
      delta = datetime.datetime.now(tz) - date
    elif isinstance(date, datetime.date):
      delta = datetime.date.today() - date
    else:
      return None

    num_years = delta.days / 365
    if num_years > 0:
        return ungettext(u"%d year ago", u"%d years ago", num_years) % num_years

    num_weeks = delta.days / 7
    if num_weeks > 0:
        return ungettext(u"%d week ago", u"%d weeks ago", num_weeks) % num_weeks

    if delta.days > 0:
        return ungettext(u"%d day ago", u"%d days ago", delta.days) % delta.days

    num_hours = delta.seconds / 3600
    if num_hours > 0:
        return ungettext(u"%d hour ago", u"%d hours ago", num_hours) % num_hours

    num_minutes = delta.seconds / 60
    if num_minutes > 0:
        return ungettext(u"%d minute ago", u"%d minutes ago", num_minutes) % num_minutes

    return ugettext(u"a few seconds ago")


@register.filter(name='timeuntil_human')
def humanize_timeuntil(date):
    if isinstance(date, datetime.datetime):
      delta = date - datetime.datetime.today()
    else:
      delta = date - datetime.date.today()

    num_years = delta.days / 365
    if num_years > 0:
        return ungettext(u"%d year", u"%d years", num_years) % num_years

    num_weeks = delta.days / 7
    if num_weeks > 1:
        return ungettext(u"%d week", u"%d weeks", num_weeks) % num_weeks

    if delta.days > 0:
        return ungettext(u"%d day", u"%d days", delta.days) % delta.days

    num_hours = delta.seconds / 3600
    if num_hours > 0:
        return ungettext(u"%d hour", u"%d hours", num_hours) % num_hours

    num_minutes = delta.seconds / 60
    if num_minutes > 0:
        return ungettext(u"%d minute", u"%d minutes", num_minutes) % num_minutes

    return ugettext(u"a few seconds")