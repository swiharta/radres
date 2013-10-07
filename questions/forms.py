from models import *
#from django.conf import settings
from django.forms import Form, BaseForm, ValidationError
from django.forms import ChoiceField, ModelChoiceField, BooleanField #IntegerField,\
#							CharField, SplitDateTimeField, CheckboxInput,FileInput,\
#							FileField, ImageField
#from django.forms import Textarea, TextInput, Select, RadioSelect,\
#							CheckboxSelectMultiple, MultipleChoiceField,\
#							SplitDateTimeWidget,MultiWidget, MultiValueField, \
#							ValidationError
#from django.forms.forms import BoundField
from django.forms.models import ModelForm
#from django.utils.translation import ugettext_lazy as _
#from django.utils.safestring import mark_safe
#from django.template import Context, loader
#from django.template.defaultfilters import slugify

#from itertools import chain
#import uuid

class UserChoiceForm(Form):
  
  def __init__(self, question, *args, **kwargs):
    self.question = question
    self.choice = None
    super(UserChoiceForm, self).__init__(*args, **kwargs)
    choice = self.fields['choice'] # unnecessary?
    choice.label = question.text
    choices = [(choice.letter, choice.text) for choice in self.question.choices.all()]
    choices.append(('',''))
    self.fields['choice'].choices = choices # default choices
    #choice.choices = choices?
  
  choice = ChoiceField(required=False)
  ignore = BooleanField(required=False)
  mark = BooleanField(required=False)


class FilterForm(Form):

#  def __init__(self, request, *args, **kwargs):
#    self.request = request
#    super(FilterForm, self).__init__(*args, **kwargs)

#  def clean(self):
##    filters = {}
##    if self.request.method == 'POST':
##      for filter in FILTERS:
##        filters[filter] = self.request.POST.get(filter)
##    else:
##      for filter in FILTERS:
##        filters[filter] = self.request.session.get(filter)
#
##    for field in self.fields:
##      if self.cleaned_data[field]:
##        pass
##      else:
##        self.cleaned_data[field] = self.request.session.get(field)
#    request = self.request
#    cleaned_data = self.cleaned_data
#    fields = self.fields
#
#    if request.method == 'POST':
#      for field in fields:
#        print 'hello'
#        cleaned_data[field] = request.POST.get(field).capitalize()
#          # I think the js / Python Boolean issue was fixed in Django 1.3
#          # https://code.djangoproject.com/changeset/16148
#    else:
#      for field in fields:
#        cleaned_data[field] = request.session.get(field)
#
#    return cleaned_data

  reset_filter = BooleanField(required=False)
  marked_filter = BooleanField(required=False)
  flagged_filter = BooleanField(required=False)
  incorrect_filter = BooleanField(required=False)
  correct_filter = BooleanField(required=False)
  unvisited_filter = BooleanField(required=False)
