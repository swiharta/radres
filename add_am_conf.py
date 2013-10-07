import os, re, codecs, sys
from datetime import datetime
from string import strip
from fuzzywuzzy import process

DIV_MAP = {
'MAGEEWOMEN\'S': 'WI',
'WOMEN\'SIMAGING': 'WI',
'PEDIATRIC': 'Peds',
'ABDOMINALIMAGING': 'AI',
'VASCULAR/INTERVENTIONAL': 'IR',
'VASCULARIMAGING': 'IR',
'NEURO-ED': 'ED',
'NEURO-RADIOLOGY': 'Neuro',
'NUCLEARMEDICINE': 'Nucs',
'NUCLEARIMAGING': 'Nucs',
'CHEST': 'Chest',
'MUSCULOSKELETAL': 'MSK',
'BODY-ED': 'ED',
}

if __name__ == "__main__":
  os.environ.setdefault("DJANGO_SETTINGS_MODULE", "radres.settings")

from radcal.models import ConfEvent, Conference

from django.core.mail import send_mail
from django.core.cache import cache
from django.utils import timezone

# File should have leading and trailing whitespace stripped
f = codecs.open(sys.argv[1], 'rU', encoding='utf-8', errors='ignore')

blocks = {}
i=-1
for line in f:
  match = re.search(r'(.*?\t)([0-9].*?\t)([\S].*?\t)(.*?\n)', line)
  if match: # 'i' skips first line!!
    day = match.group(1).strip()
    if not day in ['Sat', 'Sun']:
      _date = datetime.strptime(match.group(2).strip(),'%m/%d/%Y')
      div_raw = match.group(3).strip().replace(' ','')
      try:
        div = DIV_MAP[div_raw]
      except KeyError:
        best_match = process.extractOne(div_raw, DIV_MAP.keys())
        if best_match[1] < 73: # 'Sat' is 72% match with 'Chest'
          div = None
        else:
          div = DIV_MAP[best_match[0]]
      presenter = match.group(4).strip().capitalize()
      if div:
        blocks[i] = ([_date, div, presenter])
      else:
        print line
      i += 1

am = Conference.objects.get(abbr='am')

# confs = ConfEvent.objects.filter(conference=noon)
# confs.delete()

# for block, items in blocks.items():
##    print items
  # items[0] = datetime.strptime(items[0],'%m/%d/%Y')
  # start = datetime.combine(items[0], noon.start_time)
  # end = datetime.combine(items[0], noon.end_time)
  # ConfEvent.objects.create(date=items[0], conference=noon, 
                           # div=items[2], title=items[3],
                           # presenter = items[4], 
                           # start=start, end=end
                           # )

for block, items in blocks.items():
  # print items
  created = False
  try:
    conf, created = ConfEvent.objects.get_or_create(date=items[0], conference=am)
  except ConfEvent.MultipleObjectsReturned:
    confs = ConfEvent.objects.filter(date=items[0], conference=am)
    conf = confs[0]
    for c in confs[1:]:
        body = str(c.date) + ' - ' + c.div + c.presenter
        send_mail('AM conference deleted', body, 'swihart@radres.info', ['swihart.andrew@gmail.com'], fail_silently=False)
        c.delete()
  if not created:
    print 'Updating...%s' % conf
  conf.div = items[1]
  conf.presenter = items[2]
  conf.start = timezone.make_aware(datetime.combine(items[0], am.start_time), timezone.get_default_timezone())
  conf.end = timezone.make_aware(datetime.combine(items[0], am.end_time), timezone.get_default_timezone())
  conf.save()
  if not created:
    print 'To...%s' % conf
  else:
    print 'Created...%s' % conf

f.close()

cache.delete('ce_json')

  ## Deal with extraneous markup from Radres.info html
  # line = line.replace('\t','')

  ## Don't add blank lines to block items
  # line = line.replace('\n','')
  # if line != '' and not skip:
    # blocks[block].append(line)


# p = Page.objects.get(id=1)
# for block, items in blocks.items():
  # for item in items:
    # print item
    # c = ContentItem.objects.get_or_create(content_html=item)
    ## get_or_create generates a tuple with the object at [0] and T | F at [1]
    # PageContentItem(content_item=c[0], page=p, block_name=block).save()


## for testing


# f2 = open('crap.html', 'w')

# for block, items in blocks.items():
  # f2.write(items[0] + block + '\n')

# f2.close()