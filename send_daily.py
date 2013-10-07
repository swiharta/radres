#from django.core.management import setup_environ
#import settings
#setup_environ(settings)

import os

if __name__ == "__main__":
  os.environ.setdefault("DJANGO_SETTINGS_MODULE", "radres.settings")

#import re, sys
# from string import strip
from datetime import date, timedelta

#from django.utils.translation import ugettext as _
from django.template.loader import render_to_string#, get_template
#from django.template import Context
# from django.shortcuts import render_to_response
from django.core.mail import EmailMultiAlternatives, get_connection#, send_mail

from radcal.models import ShiftEvent

def send(text_template="radcal/email/reminder_message.txt",
         html_template="radcal/email/reminder_message.html"):
  today = date.today()
  weekday = today.weekday()
  if weekday == 4: # 4 = Friday
    this_saturday = today + timedelta(days = 1)
    this_sunday = today + timedelta(days = 2)
    dates = [today, this_saturday, this_sunday]
  elif weekday == 5 or weekday == 6:
    dates = None
  else:
    dates = [today]

  from_email = 'swihart@radres.info'
  messages = []

  for day in dates:
    day_format = day.strftime('%A, %B %d, %Y')
    subject = 'Call / Moonlighting Reminder for %s' % day_format
    events = ShiftEvent.objects.filter(date=day)
    d = { 'events': events, 'day': day }
    for event in events:
      if event.user:
        recipient_list = []
        email = getattr(event.user, 'email', None)
        if email: # handles blank and non-existent email attributes
#          recipient_list.append('swihart@radres.info')
          recipient_list.append(email)

        d.update(user=event.user)
        text_content = render_to_string(text_template, d)
        html_content = render_to_string(html_template, d)
        msg = EmailMultiAlternatives(subject, text_content, from_email, recipient_list)
        msg.attach_alternative(html_content, "text/html")
        messages.append(msg)

  connection = get_connection()
  connection.send_messages(messages)

def main():
  send()

if __name__ == '__main__':
  main()
  
