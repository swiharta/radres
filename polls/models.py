from django.db import models
from django.contrib.auth.models import User
from django_extensions.db.fields import AutoSlugField

class QuestionManager(models.Manager):
  def get_visible(self):
    return self.get_query_set().filter(publish_at__lte=datetime.datetime.now(), active=True)

class Question(models.Model):
  created_on = models.DateTimeField(auto_now_add = True)
  modified = models.DateTimeField(auto_now = True)
  active = models.BooleanField(default = True)
  user = models.ForeignKey(User, related_name="poll_%(class)ss")

  text = models.TextField()
  slug = models.SlugField(unique = True, max_length = 50)
  text = models.TextField()
  allow_multiple = models.BooleanField(default = False)

  def save(self):
    title = self.text.replace('?', '')
    title = title.replace('.', '')
    slug = '-'.join(title.split())
    count = Question.objects.filter(slug__icontains = slug).count()
    print count
    if count:
      slug += str(count+1)
    self.slug = slug
    super(Question, self).save()

def __str__(self):
  return self.text

@models.permalink
def get_absolute_url(self):
  return ('polls.views.question', [self.slug])

@models.permalink
def get_results_url(self):
  return ('polls.views.results', [self.slug])

class Meta:
  ordering = ('-created_on', )


class Choice(models.Model):
  question = models.ForeignKey(Question)
  text = models.TextField()
  total_votes = models.IntegerField(default = 0)

  def __str__(self):
    return '%s - %s' % (self.question.text, self.text)