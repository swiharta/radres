import os

if __name__ == "__main__":
  os.environ.setdefault("DJANGO_SETTINGS_MODULE", "radres.settings")

from radcal.models import *
from datetime import datetime, timedelta

se = ShiftEvent.objects.all()
for e in se:
  if not e.start:
    if e.shift.start_time >= e.shift.end_time:
      end_date = e.date + timedelta(days = 1)
    else:
      end_date = e.date
    e.start = datetime.combine(e.date, e.shift.start_time)
    e.end = datetime.combine(end_date, e.shift.end_time)
    e.save()