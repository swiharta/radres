from radres.utils import make_custom_datefield
from models import *
from django.forms import Form, BaseForm, ValidationError
from django.forms import ChoiceField, ModelChoiceField, BooleanField, DateField #IntegerField,\
#							CharField, SplitDateTimeField, CheckboxInput,FileInput,\
#							FileField, ImageField
#from django.forms import Textarea, TextInput, Select, RadioSelect,\
#							CheckboxSelectMultiple, MultipleChoiceField,\
#							SplitDateTimeWidget,MultiWidget, MultiValueField, \
#							ValidationError
from django.forms.formsets import formset_factory, BaseFormSet
from django.forms.models import modelformset_factory
from django.forms.models import ModelForm

#from django.utils.safestring import mark_safe
#from django.template import Context, loader

class ShiftChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.abbr


class ShiftForm(ModelForm):
#  formfield_callback = make_custom_datefield
  shift = ShiftChoiceField(queryset=Shift.objects.all())

  class Meta:
    model = ShiftEvent
    exclude = ('public', 'remind')

ShiftFormset = formset_factory(ShiftForm)
#ShiftFormset = modelformset_factory(ShiftEvent, can_delete=True, extra=10, exclude=('public', 'remind'))

class ConfForm(ModelForm):
#  formfield_callback = make_custom_datefield

  class Meta:
    model = ConfEvent
    exclude = ('public', 'remind')

ConfFormset = formset_factory(ConfForm)


class FilterForm(Form):

  night_call_filter = BooleanField(required=False)
  day_call_filter = BooleanField(required=False)
  ED_filter = BooleanField(required=False)
  IR_filter = BooleanField(required=False)
  moon_filter = BooleanField(required=False)
#  conflict_switch = BooleanField(required=False)

class SwitchForm(Form):

  conflict_switch = BooleanField(required=False)

# takes a 'date' object for the first day of the month for the requested calendar
#class MonthForm(Form):
#  first = DateField