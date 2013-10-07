from django import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from ajax_select.fields import AutoCompleteSelectMultipleField, AutoCompleteSelectField
from django.forms.extras.widgets import SelectDateWidget
from django.contrib.localflavor.us.forms import USPhoneNumberField

from models import Profile

import account.forms

#class SignupForm(account.forms.SignupForm):
#
#  birthdate = forms.DateField(widget=SelectDateWidget(years=range(1910, 1991)))

# Mashup form for collecting data for Profile, Account (django-user-accounts), & EmailAddress (django-user-accounts)
class SettingsForm(account.forms.SettingsForm):

  first_name=forms.CharField(
    label=_("First Name"),
    max_length=30,
    widget=forms.TextInput(),
    required=False
  )
  last_name=forms.CharField(
    label=_("Last Name"),
    max_length=30,
    widget=forms.TextInput(),
    required=False
  )
  phone=USPhoneNumberField(
    label=_("Phone Number"),
    help_text=_("Never given out!"),
    required=False
  )
  ical=forms.BooleanField(
    label=_("Enable your public calendar URL"),
    required=False
  )
  # Don't care about Timezone / Language from django-user-accounts app
  def __init__(self, *args, **kwargs):
    self.request = kwargs.pop('request', None)
    super(SettingsForm, self).__init__(*args, **kwargs)
    if self.fields['timezone']:
      del self.fields['timezone']
    if self.fields['language']:
      del self.fields['language']

    initial = getattr(self, 'initial', None)
    print initial
    if initial:
      self.fields['ical'].help_text = '<input type=text value="http://radres.info/calendar/%s" id="ical_url" style="cursor: pointer;" rel="tooltip" \
                                       title="Copy and paste into Google Calendar, iPhone Settings, etc..." readonly></input>' % self.initial['username']
    else:
      self.fields['ical'].help_text = 'http://radres.info/calendar/<username>'

class ProfileForm(forms.ModelForm):
#    def __init__(self, *args, **kwargs):
#      super(ProfileForm, self).__init__(*args, **kwargs)
#      instance = getattr(self, 'instance', None)
#      if instance:
#        self.fields['ical'].help_text = 'http://radres.info/calendar/%s' % self.instance.user.username
#      else:
#        self.fields['ical'].help_text = 'http://radres.info/calendar/<username>'

    # Email validation form authored by Daniel Greenfeld
    def clean_email(self):
#      """ Custom email clean method to make sure the user doesn't use the same email as someone else"""
      email = self.cleaned_data.get("email", "").strip()
#      if User.objects.filter(email=email).exclude(username=self.instance.user.username):
#          self._errors["email"] = self.error_class(["%s is already in use in the system" % email])
#          return ""
      return email

    class Meta:
      model = Profile
      fields = (
               'first_name',
               'last_name',
#               'short_range',
#               'long_range',
               'phone',
               'ical',
      )


class UserMessage(forms.Form): #('160','Phone'),
  length = forms.ChoiceField(label=_('To'), choices=(('80','Pager'),('500','Email')))
  message = forms.CharField(label=_("Message"), max_length=500, widget=forms.Textarea, help_text='Enter your message.')
  recipients = forms.ModelMultipleChoiceField(queryset=User.objects.all())

  def clean_message(self):
    message = self.cleaned_data.get('message')
    length = self.cleaned_data.get('length')
    return message[:int(length)]


class UserSelect(forms.Form):
  users = AutoCompleteSelectMultipleField('user-select', required=False, help_text=None)