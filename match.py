from fuzzywuzzy import process
import codecs#, re, sys
from residents import RESIDENTS, NAMES

filename = raw_input('Enter a name for the new file: ')
file = codecs.open(filename, 'w', encoding='utf-8', errors='ignore')
for resident in RESIDENTS:
  match = process.extractOne(resident, NAMES)
  name, accuracy = match[0], match[1]
#  if accuracy < 60:
#    print resident
#    name = raw_input("Enter Resident Name: ")
  s = "'%s': '%s', %s\n" % (resident, name, accuracy)
  file.write(unicode(s))
file.close()