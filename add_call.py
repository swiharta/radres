import os, re, sys
from datetime import datetime
  
if __name__ == "__main__":
  os.environ.setdefault("DJANGO_SETTINGS_MODULE", "radres.settings")

#from django.utils.translation import ugettext as _

from radcal.models import Shift, ShiftEvent
from radcal.utils import get_conflict_ids, get_last_update_time
from residents import RESIDENTS

from django.contrib.auth.models import User
from django.core.mail import send_mail, get_connection
from django.core.cache import cache
from django.utils import timezone
# import dse
# dse.patch_models(specific_models=[ShiftEvent])
# from string import strip

SHIFTS = ['CHP', 'PUH', 'SHY', 'Angio', 'EDB', 'EDN', 'MNeuro', 'Neuro',
          'Chest', 'Senior', 'Monte', 'Sports', 'Mville', 'Hillman', 'Magee']
SAT_SHIFTS = ['CHP_W', 'PUH_W', 'SHY_W', 'Angio_W', 'EDB', 'EDN', 'MNeuro', 'Neuro',
              'Chest', 'Senior', 'Monte', 'Sports_S', 'Mville_S', 'Hillman_S', 'Magee_S']


def print_cal(events):
  # pass
#  print blocks
  for event in events:
    print " - ".join(event)

def file_cal(events):
  newfile = raw_input('Enter a name for the new file: ')
  f2 = open(newfile, 'w')

  for event in events:
    f2.write(str(event) + '\n')

  f2.close()


def commit_cal(events):
  shift_objects = {}
  print 'Deleting shift events...'
  se = ShiftEvent.objects.all()
  se.delete()
  for shift in set(SHIFTS + SAT_SHIFTS):
    shift_objects[shift] = Shift.objects.get(code=shift)
  
  dummy = User.objects.get(id=16) # default to some resident
  username = None
  # with ShiftEvent.delayed as d:
  for event in events:
    last_name = event[2]
    try:
      username = RESIDENTS[last_name.lower()] # do the lower() here so I can store the un-lower() as resident
      try:
        user = User.objects.get(username=username)
      except User.DoesNotExist:
        user = dummy
    except KeyError:
      subject = 'Misspelled last name: "' + last_name + '"'
      send_mail(subject, subject, 'swihart@radres.info', ['swihart.andrew@gmail.com'], fail_silently=False)
      user = dummy
      # TODO: If date upcoming soon, send email to everyone about the error and the name
    # d.insert(dict(date = event[0], shift=shift_objects[event[1]], resident=event[2], user=user))
    print 'Saving %s...' % (str(event))
    ShiftEvent.objects.create(date=event[0], shift=shift_objects[event[1]], resident=last_name, user=user)
  get_conflict_ids(force_refresh=True)
  get_last_update_time()

def update_cal(events):
  shift_objects = {}
  for shift in set(SHIFTS + SAT_SHIFTS):
    shift_objects[shift] = Shift.objects.get(code=shift)
  
  # with ShiftEvent.delayed as d:
  for event in events:
    last_name = event[2]
    shift = shift_objects[event[1]]
    if not last_name: # blank cell in the Excel file
      try:
        target_event = ShiftEvent.objects.get(date=event[0], shift=shift)
        target_event.delete() # delete so it doesn't show up on the calendar
        print "Deleted...%s" % (str(target_event))
      except ShiftEvent.DoesNotExist: # most blanks are permanently blank and there will be no existing event
        # unfortunately I had to add this even though it will result in exceptions being raised
        # to account for when they decide to eliminate a shift, such as the Hillman Saturdays
        print 'This shift event does not exist'
        pass
    else:
      if '/' in last_name: # take the first name if two are given to assign at least one user
        last_name = last_name.split('/')[0]
      username = RESIDENTS.get(last_name.lower().translate(None, '0123456789,').strip(), 'unknown') # do the lower() here so I can store the un-lower() as resident
      try:
        user = User.objects.get(username=username)
      except User.DoesNotExist:
        user = None
      if username == 'unknown':
        subject = 'Misspelled last name: "' + last_name + '"'
        send_mail(subject, subject, 'swihart@radres.info', ['swihart.andrew@gmail.com'], fail_silently=False)
        user = None
      # TODO: If date upcoming soon, send email to everyone about the error and the name
      created = False
      try:
        target_event, created = ShiftEvent.objects.get_or_create(date=event[0], shift=shift)
      except ShiftEvent.MultipleObjectsReturned:
        shifts = ShiftEvent.objects.filter(date=event[0], shift=shift)
        target_event = shifts[0]
        for s in shifts[1:]:
          body = str(s.date) + ' - ' + s.shift.name + ' - ' + s.resident
          send_mail('Shift event deleted', body, 'swihart@radres.info', ['swihart.andrew@gmail.com'], fail_silently=False)
          s.delete()
      if not created:
        print 'Updating %s...' % (str(target_event))
      target_event.resident=event[2] # the exact string from each cell in Excel
      target_event.user=user
      target_event.start = timezone.make_aware(datetime.combine(event[0], shift.start_time), timezone.get_default_timezone())
      target_event.end = timezone.make_aware(datetime.combine(event[0], shift.end_time), timezone.get_default_timezone())
      target_event.save()
      if not created:
        print 'To %s...' % (str(target_event))
      else:
        print 'Created...%s' % (str(target_event))
    # d.insert(dict(date = event[0], shift=shift_objects[event[1]], resident=event[2], user=user))

  get_conflict_ids(force_refresh=True)
  get_last_update_time()
  
  cache.delete('se_json')

    
def process_cal(filename, option):
  f = open(filename, 'rU')

  sample = f.readline() # reads first line, the "cursor" is advanced in the file
  f.seek(0) # reset the "cursor"
#  tabs = sample.count("\t")
#  re_pattern = '(.*?\t)' * tabs + '(.*?\n)'
#  count = tabs + 1
  tabs = sample.count("\t")
  re_pattern = '(.*?\t)' * tabs + '(.*?\n)'

  ## debugging stuff
  print "\nFound %d pieces of data in the first line:\n\n %s" % (tabs, sample)
#  x = bool(raw_input("Press enter to continue..."))
#  if x:
#    sys.exit("\nGoodbye, let's do this again soon.")
  print "\nUsing regex pattern:\n", repr(re_pattern), "\n"

  rows = []

  # For each line, append each tab-delimited element to a list, then append that list
  # to the big "blocks" list. We'll deal with what each element represents later.

  for line in f:
    if line.strip():
      match = re.search(re_pattern, line)
      if match:
        row = [match.group(i+1).translate(None, '\t"').strip() for i in range(tabs)]
        # i = 1
        # while i < count: # get all but the last element
          # from http://stackoverflow.com/questions/10017147/python-replace-characters-in-string
          # can use str.translate(None, '\t,"') or re.sub('[\t,"]', '', str)
          # old way: .replace('\t','').replace(',','').replace('"','').strip())
          # row.append(match.group(i).translate(None, '\t,"').strip())
          # `"` surrounds names with commas in tha tab-separated .txt file generated by Excel
          # row.append(match.group(i).translate(None, '\t,"').strip().strip())
            # strip gets rid of blank spaces in blank shifts, added so that leading tabs are created in Excel
          # i += 1
        # row.append(match.group(i).translate(None, '\t,"').strip().strip()) # include the last element
        # if day != "Sat" and day != "Sun":
        rows.append(row)
      else:
        send_mail('Line skipped', line, 'swihart@radres.info', ['swihart.andrew@gmail.com'], fail_silently=False)



  # Let's clean up the data a little bit
  ######################################

  events = []
  for row in rows:
    date_ = datetime.strptime(row[0],'%m/%d/%y')
    x = -1
    for resident in row[2:]:
      x += 1
      if date_.weekday() in [5 ,6]: # 5 = Saturday in Europe (monday first)
        events.append([date_, SAT_SHIFTS[x], resident])
      else:
        events.append([date_, SHIFTS[x], resident])

  if option == '--print':
    print_cal(events)
  elif option == '--file':
    file_cal(events)
  elif option == '--commit':
    commit_cal(events)
  elif option == '--update':
    update_cal(events)

  f.close()


def main():
  if len(sys.argv) != 3:
    print 'usage: ./add_call.py {--print | --file | --commit | --update} file'
    sys.exit(1)

  option = sys.argv[1]
  filename = sys.argv[2]
  process_cal(filename, option)
  if option == '--print' or '--file' or '--commit' or '--update':
    pass
  else:
    print 'unknown option: ' + option
    sys.exit(1)

if __name__ == '__main__':
  main()