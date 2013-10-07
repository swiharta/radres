from django.db import models
from django.utils.translation import ugettext, ugettext_lazy as _

from django.contrib.auth.models import User

DIV_CHOICES = (
  ('GI', 'Gastrointestinal'),
  ('GU', 'Genitourinary'),
  ('Peds', 'Pediatric Imaging'),
  ('Physics', 'Radiologic Physics'),
  ('VIR', 'Vascular / Interventional'),
  ('MSK', 'Musculoskeletal'),
  ('Nucs', 'Nuclear Medicine'),
  ('Mammo', 'Mammography'),
  ('Chest', 'Chest Imaging'),
  ('ENT', 'Head and Neck'),
  ('Neuro', 'Neuroradiology'),
  ('Cardiac', 'Cardiac Imaging'),
  ('WI', 'Women\'s Imaging'),
)

#class QuestionManager(models.Manager):
#  def get_public(self):
#    return self.get_query_set().filter(public=True)

class Question(models.Model):
  created = models.DateTimeField(_('created'), auto_now_add=True)
  modified = models.DateTimeField(_('modified'), auto_now=True)
  years = models.CharField(_('question years'), max_length=100, blank=True)
  set = models.CharField(_('question set'), max_length=100, blank=True)
  div = models.CharField(_('subdivision'), max_length=8, choices=DIV_CHOICES, blank=True)
  text = models.TextField(_('question text'))
  
#  objects = QuestionManager()

  def __unicode__(self):
    return self.text

class Choice(models.Model):
  letter = models.CharField(max_length=1)
  text = models.TextField(_('choice text'))
  question = models.ForeignKey(Question, related_name='%(class)ss')

  def correct(self):
    answers = self.question.answers.all()
    answer_choices = [answer.choice for answer in answers]
    return self in answer_choices

  correct.short_description = 'Correct'
  correct.admin_order_field = 'correct'

  def __unicode__(self):
    return self.text
    
class Answer(models.Model):
  created = models.DateTimeField(_('created'), auto_now_add=True)
  modified = models.DateTimeField(_('modified'), auto_now=True)
  user = models.ForeignKey(User, null=True, blank=True)
  text = models.TextField(_('answer text'), default='No explanation given')
  choice = models.ForeignKey(Choice, related_name='%(class)ss', blank=True, null=True)
  question = models.ForeignKey(Question, related_name='%(class)ss')

  def __unicode__(self):
    return self.text

class UserChoice(models.Model):
  created = models.DateTimeField(_('created'), auto_now_add=True)
  modified = models.DateTimeField(_('modified'), auto_now=True)
  choice_date = models.DateTimeField(_('choice made'), blank=True, null=True)
  ignore = models.BooleanField(default=False)
  mark = models.BooleanField(default=False)
  user = models.ForeignKey(User)
  choice = models.ForeignKey(Choice, blank=True, null=True)
  question = models.ForeignKey(Question)

  def correct(self):
    return self.choice.correct()

#  def __unicode__(self): causes a multiple database hits for some reason
#    return '%s' % self.user.username