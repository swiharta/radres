import json

from django.conf import settings
# from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
# from django.db.models import Q
# from django.utils.translation import ugettext_lazy as _
# from django.utils.translation import ugettext
# from django.contrib import auth, messages
from django.views.generic import ListView, DetailView

# from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
# from django.shortcuts import redirect
from django.template.loader import render_to_string

# from avatar.templatetags.avatar_tags import avatar

if "notification" in settings.INSTALLED_APPS:
  from notification import models as notification
else:
  notification = None
from radres.utils import get_send_mail
send_mail = get_send_mail()

#from django.views.generic.edit import FormView
from account.mixins import LoginRequiredMixin
from account.models import EmailAddress
import account.views

from radprofile.forms import ProfileForm, UserMessage, UserSelect
from radprofile.models import Profile
from radres.views import CreateOrUpdateView
import radprofile.forms


class ProfileListView(ListView):
  """
  List all profiles of a given type (or the default type, if
  profile_slug is not given.)

  If all_profiles is set to True, all profiles are listed.
  """
  context_object_name = "users"
  all_profiles = False

  def get_queryset(self):
    profiles = Profile.objects.select_related()
    profiles = profiles.order_by("-date_joined")

    search_terms = self.request.GET.get("search", "")
    order = self.request.GET.get("order", "date")

    if search_terms:
      profiles = profiles.filter(user__username__icontains=search_terms)
    if order == "date":
      profiles = profiles.order_by("-user__date_joined")
    elif order == "name":
      profiles = profiles.order_by("user__username")

    return profiles

  def get_context_data(self, **kwargs):
    search_terms = self.request.GET.get("search", "")
    order = self.request.GET.get("order", "date")
    user_select = UserSelect(self.request.POST or None, initial={'users':[self.request.user.id]})

    ctx = {
      "order": order,
      "search_terms": search_terms,
      "user_select": user_select,
      }
    ctx.update(super(ProfileListView, self).get_context_data(**kwargs))

    return ctx


class ProfileDetailView(DetailView):

  model = Profile
  slug_field = 'username'

  def get_context_data(self, **kwargs):
    this_user = get_object_or_404(User, username=self.kwargs["slug"])
    is_me = self.request.user == this_user

    ctx = {
      "is_me": is_me,
      "this_user": this_user,
      }
    ctx.update(super(ProfileDetailView, self).get_context_data(**kwargs))

    return ctx

class PasswordResetView(account.views.PasswordResetView):

  def get_context_data(self, **kwargs):
    ctx = { "DEFAULT_FROM_EMAIL": settings.DEFAULT_FROM_EMAIL}
    ctx.update(super(PasswordResetView, self).get_context_data(**kwargs))
    return ctx

@login_required
def user_profile(request, username, template_name='radprofile/profile_facebox.html', **kwargs):
  if request.is_ajax():
    template_name = 'radprofile/profile_facebox.html'

  user = User.objects.get(username=username)
  is_me = (request.user == user)
  
  try:
    profile = user.get_profile()
  except Profile.DoesNotExist:
    raise Exception

  redirect_to = request.REQUEST.get('next', '')
  message_form = UserMessage(request.POST or None, initial={'recipients':[user]}) # when you add more recipients, make sure this isn't screwing it up
  if message_form.is_valid():
    #        messages.add_message(request, messages.SUCCESS, ugettext("Your profile has been updated."))
    subject = 'RadRes message from ' + request.user.profile.get_full_name()
    message = message_form.cleaned_data['message']
    from_email = request.user.get_profile().email
    recipient_list = []
    paging = message_form.cleaned_data['length'] == '80'
    if paging:
      subject = ''
      for user in message_form.cleaned_data['recipients']:
        profile = user.get_profile()
        long_range_digits = str(profile.long_range).replace('-','')
        recipient_list.append(long_range_digits + '@usamobility.net')
    else:
      for user in message_form.cleaned_data['recipients']:
        profile = user.get_profile()
        recipient_email = profile.email
        recipient_list.append(recipient_email)
    send_mail(subject, message, from_email, recipient_list)
    if request.is_ajax():
      return HttpResponse(u'Your message was sent successfully.')
    else:
      return HttpResponseRedirect(redirect_to)
  
    
  return render_to_response(template_name, dict({
    "is_me": is_me,
    "profile": profile,
    "message_form": message_form,
    "redirect_to": redirect_to
    }), context_instance=RequestContext(request))


@login_required
def profile_edit(request, form_class=ProfileForm, **kwargs):
  template_name = kwargs.get("template_name", "radprofile/profile_edit.html")
  redirect_to = request.REQUEST.get('next', '')
  try:
    profile = request.user.get_profile()
  except Profile.DoesNotExist:
    profile = Profile.objects.create(user=request.user,
                                     username=request.user.username,
                                     email=request.user.email
    )
  profile_form = form_class(request.POST or None, instance=profile)

  if profile_form.is_valid():
    profile = profile_form.save(commit=False)
    profile.user = request.user
    profile.save()
    #        messages.add_message(request, messages.SUCCESS, ugettext("Your profile has been updated."))
    if request.is_ajax():
      return HttpResponse(u'success')
    else:
      return HttpResponseRedirect(redirect_to)
  if request.is_ajax():
    data = {
      "html": render_to_string(
        template_name,
        RequestContext(request, { 'form': profile_form, } )
      )
    }
    return HttpResponse(json.dumps(data), mimetype="application/json")
  return render_to_response(template_name, {
    "profile": profile,
    "form": profile_form,
    "redirect_to": redirect_to,
    }, context_instance=RequestContext(request))


# Currently unused, now using "mashup" SettingsView
class ProfileView(LoginRequiredMixin, CreateOrUpdateView):

  model = Profile
  template_name = "radprofile/profile_edit.html"
  form_class = ProfileForm
  redirect_field_name = "next"

# `queryset` should match a single model instance (letting get() run the final query later)
  def get_object(self, queryset=None):
    queryset = Profile.objects.filter(user=self.request.user)
    return super(ProfileView, self).get_object(queryset=queryset)

  def get_fragments(self):
    try:
      full_name = self.request.user.profile.get_full_name()
    except Profile.DoesNotExist:
      full_name = None
    if full_name:
      fragments = {"#navbarFullname": '<span id="navbarFullname" class="no-narrow">%s</span>' % self.request.user.profile.get_full_name(), }
      return fragments
    return None

class SettingsView(account.views.SettingsView):

  form_class = radprofile.forms.SettingsForm

  def get_form_class(self):
    # @@@ django: this is a workaround to not having a dedicated method....(see original app)
    self.primary_email_address = EmailAddress.objects.get_primary(self.request.user)
    try:
      self.profile = self.request.user.get_profile()
    except ObjectDoesNotExist:
      self.profile = None
    return super(SettingsView, self).get_form_class()

  def get_initial(self):
    initial = super(SettingsView, self).get_initial()
    if self.profile:
      initial["first_name"] = self.profile.first_name
      initial["last_name"] = self.profile.last_name
      initial["phone"] = self.profile.phone
      initial["ical"] = self.profile.ical
    initial["username"] = self.request.user.username
    return initial

  def update_settings(self, form):
    ## update_settings() gets called from form_valid()
    self.update_email(form)
    self.update_account(form)
    self.update_profile(form)

  def update_profile(self, form):
    user = self.request.user
    if not self.profile:
      self.profile = Profile.objects.create(user=user, username=user.username)
    fields = {}
    if "first_name" in form.cleaned_data:
      fields["first_name"] = form.cleaned_data["first_name"]
    if "last_name" in form.cleaned_data:
      fields["last_name"] = form.cleaned_data["last_name"]
    if "phone" in form.cleaned_data:
      fields["phone"] = form.cleaned_data["phone"]
    if "ical" in form.cleaned_data:
      fields["ical"] = form.cleaned_data["ical"]
    if fields:
      for k, v in fields.iteritems():
        setattr(self.profile, k, v)
      self.profile.save()

  def get_fragments(self):
    try:
      full_name = self.request.user.profile.get_full_name()
    except Profile.DoesNotExist:
      full_name = None
    if full_name:
      fragments = {"#navbarFullname": '<span id="navbarFullname" class="no-narrow">%s</span>' % self.request.user.profile.get_full_name(), }
      return fragments
    return None