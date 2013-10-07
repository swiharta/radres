import json

from django.http import HttpResponse, HttpResponseBadRequest
from django.template.loader import render_to_string
#from django.contrib import auth, messages
#from django.shortcuts import redirect
from django.views.generic.detail import SingleObjectTemplateResponseMixin
from django.views.generic.edit import ModelFormMixin, ProcessFormView
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

#import radres.forms


# This is tailored for interacting with bootstrap-ajax.js
class CreateOrUpdateView(SingleObjectTemplateResponseMixin, ModelFormMixin, ProcessFormView):
  """
  View for creating or updating an object instance,
  with a response rendered by template.
  """
  template_name_suffix = '_form'

  def get(self, request, *args, **kwargs):
    self.get_object()
    form_class = self.get_form_class()
    form = self.get_form(form_class)
    if self.request.is_ajax():
      data = {
        "html": render_to_string(
          self.template_name,
          self.get_context_data(form=form, request=self.request)
          )
        }
      return HttpResponse(json.dumps(data), mimetype="application/json")
    return super(CreateOrUpdateView, self).get(request, *args, **kwargs)

  def post(self, request, *args, **kwargs):
    self.get_object()
    return super(CreateOrUpdateView, self).post(request, *args, **kwargs)

  def get_object(self, queryset=None):
    if queryset:
      try:
        self.object = queryset.get()
      except ObjectDoesNotExist:
        self.object = None
      except MultipleObjectsReturned: # need to do something better here
        self.object = None
      return object
    else:
      return None

  def form_valid(self, form):
    self.object = form.save()
    if self.request.is_ajax():
      data = {
        "html": render_to_string(
          self.template_name,
          self.get_context_data(form=form, request=self.request)
          ),
          "fragments": self.get_fragments(),
        }
      return HttpResponse(json.dumps(data), mimetype="application/json")
    return super(CreateOrUpdateView, self).form_valid(form)

  def form_invalid(self, form):
    if self.request.is_ajax():
      data = {
        "html": render_to_string(
          self.template_name,
          self.get_context_data(form=form, request=self.request)
          ),
        }
      return HttpResponseBadRequest(json.dumps(data), mimetype="application/json")
    return super(CreateOrUpdateView, self).form_invalid(form)

  def get_fragments(self):
    return None