import sys
import hashlib
import codecs
#from datetime import date

#from django.core.management import setup_environ
#import settings
#setup_environ(settings)

import os
from itertools import groupby
from django.utils.datastructures import SortedDict

if __name__ == "__main__":
  os.environ.setdefault("DJANGO_SETTINGS_MODULE", "radres.settings")

#import re, sys
# from string import strip
from datetime import date, datetime, timedelta

#from django.utils.translation import ugettext as _
from django.template.loader import render_to_string#, get_template
from radcal.models import ShiftEvent, Shift

def group_by_date_sorted(events):
  field = lambda event: event.date
  return SortedDict( # keeps dates (keys) in order in the template for loop
    [(date, list(items)) for date, items in groupby(events, field)]
  )

shifts = Shift.objects.all()
shifts_sorted = [
  shifts.filter(initials='CHP'),
  shifts.filter(initials='PUH'),
  shifts.filter(initials='SHY'),
  shifts.filter(initials='IR'),
  shifts.filter(initials='EB'),
  shifts.filter(initials='EN'),
  shifts.filter(initials='MN'),
  shifts.filter(initials='N'),
  shifts.filter(initials='Che'),
  shifts.filter(initials='Sen'),
  shifts.filter(initials='Mt'),
  shifts.filter(initials='Sp'),
  shifts.filter(initials='Mv'),
  shifts.filter(initials='H'),
  shifts.filter(initials='Mg'),
  ]

def make():
  if date.today().month > 6:
    start_year = date.today().year
  else:
    start_year = date.today().year - 1
  start = datetime.strptime('07-01-' + str(start_year), '%m-%d-%Y').date()
  end = datetime.strptime('06-30-' + str(start_year+1), '%m-%d-%Y').date()
  shift_events = ShiftEvent.objects.filter(date__gte=start, date__lte=end).order_by('date').select_related()
  day_events = group_by_date_sorted(shift_events)
  f = codecs.open('call_gen.txt', 'w', encoding='utf-8', errors='ignore')
  for event_date, events in day_events.items():
    f.write(event_date.strftime('%m/%d/%y') + '\t')
    f.write(event_date.strftime('%a') + '\t')
    for shifts in shifts_sorted:
      event_exists = False
      for event in events:
        if event.shift in shifts:
          if "," in event.resident:
            f.write('"' + event.resident + '"\t')
          else:
            f.write(event.resident + '\t')
          event_exists = True
      if not event_exists:
        f.write(' \t') # includes space as in the little Excel .txt export hack for blank cell preservation
      #   for event in value:
    f.write(' \n')
  f.close()

def get_diff():
#taken from http://stackoverflow.com/a/3544400/416687
  f = []
  lines = []
  f.append(codecs.open(sys.argv[2], 'r', encoding='utf-8', errors='ignore'))
  if sys.argv[2].split('.')[0] == 'call' or len(sys.argv) == 2:
    old_data_filename = 'call_gen.txt'
  else:
    old_data_filename = sys.argv[1]
  f.append(codecs.open(old_data_filename, 'r', encoding='utf-8', errors='ignore'))
  for i in range(2):
    # open the files named in the command line
    # stores the hash value and the line number for each line in file i
    lines.append({})
    # assuming you like counting lines starting with 1
    counter = 1
    while 1:
      # assuming default encoding is sufficient to handle the input file
      line = f[i].readline().encode('utf-8').rstrip('\r\n')
      if not line: break
      hashcode = hashlib.sha512(line).hexdigest()
      #    lines[i][hashcode] = sys.argv[1+i]+': '+line#str(counter)
      lines[i][hashcode] = line#str(counter)
      counter += 1
  #unique0 = [x for x in lines[0].keys() if x not in lines[1].keys()]
  unique1 = [x for x in lines[0].keys() if x not in lines[1].keys()]

  #for x in unique0:
  #  print lines[0][x]
  #fu = open(sys.argv[1].split('.')[0] + '_diff' + date.today().strftime('%m-%d-%Y') + '.txt', 'w')
  fu = open(sys.argv[2].split('.')[0] + '_diff.txt', 'w')
  for x in unique1:
    fu.write(lines[0][x] + '\n')
    print repr(lines[0][x])
  fu.close()

def main():
  # if len(sys.argv) == 2: # get_changed_lines.py counts as one of the arguments
  if sys.argv[2].split('.')[0] == 'call' or len(sys.argv) == 2:
    make()
  get_diff()

if __name__ == '__main__':
  main()
  # usage:  ./get_changed_lines.py file.txt [old_file.txt]'
  # file_gen.txt is created dynamically from the database
  # if you specify an old_file, no dynamic file generation is done