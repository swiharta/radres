from datetime import datetime
#import os, re

from django.utils import simplejson
#from django.db.models import Q
#from django.db import models
# from django.db.models import Q
# from django.conf import settings

from django.core.cache import cache
from django.contrib.auth.decorators import login_required, permission_required
# from django.contrib.admin.views.decorators import staff_member_required
# from django.contrib.auth.views import redirect_to_login
from django.http import HttpResponseRedirect, HttpResponse, Http404, HttpResponseNotFound
from django.core.urlresolvers import reverse
#from django.core.paginator import Paginator
#from django.template import loader, RequestContext
from django.shortcuts import get_object_or_404, render_to_response
# from django.utils.translation import ugettext_lazy as _
#from django.views.decorators.cache import cache_page
from django.views.generic.list_detail import object_list, object_detail
#from django.views.generic.simple import direct_to_template

from forms import *
from models import *
# from django.db.models import get_model
# from django.middleware.csrf import get_token
# from django.template.defaultfilters import escape
#from django.core.exceptions import ObjectDoesNotExist

SESSION_FILTER_KEYS = { # with kwargs as needed for building querysets
  'flagged_filter': 'userchoice__ignore',
  'marked_filter': 'userchoice__mark',
  'unvisited_filter': None,
  'incorrect_filter': None,
  'correct_filter': None,
  #'commented',
  #'rated'
}

@login_required
def user_filters(request):
  filters = {}
  if request.method == 'GET':
    for filter in SESSION_FILTER_KEYS:
      filters[filter] = request.session.get(filter)
      if not filters[filter]:
        del filters[filter]
    return filters
  if request.method == 'POST':
    filter_form = FilterForm(data=request.POST)
#    print filter_form.errors
    if filter_form.is_valid(): # converted javascript 'false' to False / 'true' to True (?)
#      print 'valid form'
#      print filter_form.cleaned_data
      for filter in SESSION_FILTER_KEYS:
        request.session[filter] = filter_form.cleaned_data[filter]
      filters = filter_form.cleaned_data
#      cache.delete('qset' + str(request.user.id))
    else:
      if request.is_ajax():
        return HttpResponse(u'failure')
    if request.is_ajax():
      return HttpResponse(simplejson.dumps(filters), mimetype="application/json")
    else:
      return HttpResponseRedirect(reverse("question_index"))


@login_required
def user_question_qsets(request):
  user = request.user

  qsets = {}

  UC_CACHE_KEYS = {
    'userchoices': UserChoice.objects.filter(user=user).values_list('id', flat=True),
    'answered_userchoices': UserChoice.objects.filter(user=user, choice__isnull=False).values_list('id', flat=True),
    'correct_userchoices': UserChoice.objects.filter(user=user, choice__answers__isnull=False).values_list('id', flat=True),
  }

  for key, value in UC_CACHE_KEYS.items():
    qsets[key] = cache.get(key + str(user.id)) # make different cache keys for each user

    if not qsets[key]:
      cache.set(key + str(user.id), value, 30)
      qsets[key] = value
#    qsets[key] = value # for ignoring the cache

  Q_CACHE_KEYS = {
    'marked': Question.objects.filter(userchoice__in=qsets['userchoices'], userchoice__mark=True).values_list('id', flat=True),
    'flagged': Question.objects.filter(userchoice__in=qsets['userchoices'], userchoice__ignore=True).values_list('id', flat=True),
    'correct': Question.objects.filter(userchoice__in=qsets['correct_userchoices']).values_list('id', flat=True),
    'answered': Question.objects.filter(userchoice__in=qsets['answered_userchoices']).values_list('id', flat=True),
    'unvisited': Question.objects.exclude(userchoice__in=qsets['userchoices']).values_list('id', flat=True), # TODO: make changes for paging
      # 'unvisited' should get trested like the other filters, first we need to make an 'excludes' dictionary
  }

  for key, value in Q_CACHE_KEYS.items():
    qsets[key] = cache.get(key + str(user.id))

    if not qsets[key]:
      cache.set(key + str(user.id), value, 30)
      qsets[key] = value
#    qsets[key] = value # for ignoring the cache

#  for qset, values in qsets.items():
#    print '%s: %s' % (qset, values)
  return qsets


@login_required
def question_index(request, *args, **kw):
  qsets = user_question_qsets(request)
  return question_list(request, qsets=qsets)


@login_required
def question_list(request, qsets=None, *args, **kw):
  filters = user_filters(request) # get question filters from request.session keys
  qsets = qsets
  qset = get_qset(request, qsets, filters)

#  context = {}
  context = qsets
  context['filters'] = filters

  if request.is_ajax():
    return object_list(request, queryset=qset, template_name='questions/question_list.html',
                       template_object_name='question', extra_context = context)
  else:
    filter_form = FilterForm(initial=filters)
    context['filter_form'] = filter_form

    percentage = 0
    if context.get('answered'): # prevent ZeroDivisionError for new users
      percentage = int(100 * context['correct'].count() / context['answered'].count())
    context['percentage'] = percentage

    return object_list(request, queryset=qset, template_name='questions/question_index.html',
                       template_object_name='question', extra_context = context)


@login_required
def get_qset(request, qsets, filters):
  filters = filters
  qsets = qsets

  lookups = {}
  excludes = {}
  qids = None
  filter_list = []

  if filters:
#    print filters
    for filter, value in filters.items():
      if not value: # don't include False filters in lookups
        del filters[filter]
      else:
        if filter == 'unvisited_filter': # if 'unvisited', quit and return qset immediately
          qids = qsets['unvisited'].order_by('id')
        else:
          if filter == 'incorrect_filter':
            lookups['userchoice__in'] = qsets['answered_userchoices']
            excludes['userchoice__in'] = qsets['correct_userchoices']
          elif filter == 'correct_filter':
            lookups['userchoice__in'] = qsets['correct_userchoices']
          else: # now the session keys with associated lookup statements
            if not lookups.get('userchoice__in'):
              lookups['userchoice__in'] = qsets['userchoices'] # userchoice must exist for anything but 'unvisited'
            lookups[SESSION_FILTER_KEYS[filter]] = value
        filter_list.append(filter.replace('_filter',''))
#        filter_string = ' '.join(filter_list)
    cache.set('filters' + str(request.user.id), filter_list, 2592000)
#    print filters
#  print lookups
#  print excludes

  if not qids:
    qids = Question.objects.filter(**lookups).exclude(**excludes)\
            .values_list('id', flat=True).order_by('id')

  qset = Question.objects.filter(id__in=qids).order_by('id')[:100]
  cache.set('qids' + str(request.user.id), qids, 2592000)

  return qset


@login_required
def question(request,question_id,
  		template_name='questions/question.html', *args, **kw):
#  question = get_object_or_404(Question.objects.select_related(),id=question_id) # didn't reduce queries
  question = get_object_or_404(Question,id=question_id)
  choices = question.choices.all().order_by('letter')
  user = request.user

  try:
    userchoice = UserChoice.objects.get(user=user, question=question)
  except UserChoice.DoesNotExist:
    userchoice = None

  filters = cache.get('filters' + str(user.id))
  print filters

  qset = Question.objects.all()

  qids = cache.get('qids' + str(user.id))
  if not qids:
    qids = qset.values_list('id', flat=True)

  qids = list(qids)
  # print qids
  try:
    this_qid = qids.index(question.id) # except for manually entering qid in url (outside of filtered qids), but still let view question
#    print this_qid
    next_index = this_qid + 1
    prev_index = this_qid - 1
    try:
      next_id = qids[next_index]
    except IndexError:
      next_id = qids[0]
    try:
      prev_id = qids[prev_index]
    except IndexError:
      prev_id = qids.reverse()[0]
  except ValueError:
    print 'no question id retrieved'
    next_id = None
    prev_id = None

  if userchoice:
    ucform = UserChoiceForm(question, initial={#'choice': letter,
              'ignore': userchoice.ignore, 'mark': userchoice.mark})
              # took out choice to help with JS logic on clicking non-choice but still submitting form
  else:
    ucform = UserChoiceForm(question)
  return object_detail(request,queryset=qset, object_id=question_id,
  						template_name=template_name, template_object_name = 'question',
  						extra_context = {'next_id':next_id,	'prev_id':prev_id, 'ucform':ucform,
              'choices':choices, 'userchoice':userchoice, 'filters':filters})


@login_required
def answers(request,question_id,
  		template_name='questions/answers.html', *args, **kw):
  question = get_object_or_404(Question,id=question_id)
  return object_list(request,
                       **{ 'queryset': Answer.objects.filter(question=question),
                           'template_name':template_name, 'template_object_name': 'answer' }
  )

@login_required
def userchoice(request, question_id):
  question = get_object_or_404(Question, id=question_id)
  if request.method == 'POST':
    ucform = UserChoiceForm(question, data=request.POST)
#    print 'form submitted'
    if ucform.is_valid():
#      print 'form is valid'
      userchoice, created = UserChoice.objects.get_or_create(question=question, user=request.user)
      mark = ucform.cleaned_data['mark']
      choice_letter = ucform.cleaned_data['choice']
      ignore = ucform.cleaned_data['ignore']
      if ignore == 'true':
        ignore = True
      elif ignore == 'false':
        ignore = False
      if mark == 'true':
        mark = True
      elif mark == 'false':
        mark = False
      if choice_letter.strip(): # choice actually submitted (rather than just ignore / mark)
        choice = get_object_or_404(Choice, question=question, letter=choice_letter)
        userchoice.choice = choice
        userchoice.choice_date = datetime.now()
      userchoice.ignore = ignore
      userchoice.mark = mark
      userchoice.save()
      if request.is_ajax():
        response_data = {}
        if choice_letter:
          response_data['letter'] = choice.letter
          try:
            answer_letters = [answer.choice.letter for answer in choice.question.answers.all() if answer.choice.letter]
          except:
            answer_letters = ['z']
          response_data['answer_letters'] = answer_letters
            # later we should send back a list of accepted answers and highlight them all on choice submit
        response_data['ignore'] = ignore
        response_data['mark'] = mark
        return HttpResponse(simplejson.dumps(response_data), mimetype="application/json")
    else:
      return HttpResponse(u'failure')
