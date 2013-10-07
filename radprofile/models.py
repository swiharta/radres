from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.localflavor.us.models import PhoneNumberField
from django.core.urlresolvers import reverse

class Profile(models.Model):
    """ Normalization breaking profile model authored by Daniel Greenfield """
    
    user = models.OneToOneField(User)
    email = models.EmailField(_("Email"), help_text=_("Never given out!"), max_length=30, blank=True)
    first_name = models.CharField(_("First Name"), max_length=30, blank=True)
    last_name = models.CharField(_("Last Name"), max_length=30, blank=True)
    grad_year = models.IntegerField(_("Graduation Year"), max_length=4, null=True, blank=True)
    short_range = models.IntegerField(_("Short Range Pager"), max_length=5, null=True, blank=True)
    long_range = PhoneNumberField(_("Long Range Pager"), max_length=12, blank=True)
    phone = PhoneNumberField(_("Phone Number"), help_text=_("Never given out!"), max_length=12, blank=True)
    ical = models.BooleanField(_("Public iCal feed"), default=True)

    # username field notes:
    #     used to improve speed, not editable! 
    #     Never changed after original auth.User and profiles.Profile creation!
    username = models.CharField(_("User Name"), editable=False, max_length=30)

    def save(self, **kwargs):
        """ Override save to always populate changes to auth.user model """
        user_obj = self.user
        user_obj.first_name = self.first_name
        user_obj.last_name = self.last_name
#        user_obj.email = self.email # now handled by django-user-accounts
        user_obj.save()
        super(Profile,self).save(**kwargs)

    def get_full_name(self):
        """ Convenience duplication of the auth.User method """
        return "{0} {1}".format(self.first_name, self.last_name)

#    @models.permalink
#    def get_absolute_url(self):
#        return "profile_detail", (), {"username": self.username}

    def get_absolute_url(self):
        return reverse("profile_detail", kwargs={
            "username": self.user.username
        })

    def __unicode__(self):
        return self.username