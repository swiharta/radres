from django.db import models

class Subspecialty(models.Model):
  name = models.CharField(max_length=40)
  slug = models.SlugField(unique=True)
  abbr = models.CharField(max_length=8)

  class Meta:
    ordering = ['name']

  def __unicode__(self):
    return self.name
