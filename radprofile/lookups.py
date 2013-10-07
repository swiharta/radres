#from radprofile.models import Profile
from django.contrib.auth.models import User
from django.db.models import Q
from ajax_select import LookupChannel
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
from radcal.models import Shift
from itertools import chain

class UserLookup(LookupChannel):
  model = User
  def get_query(self, q, request):
#    user_qset = User.objects.filter(Q(first_name__icontains=q) | Q(last_name__icontains=q))
#    shift_qset = Shift.objects.filter(name__icontains=q)
#    chained_qsets = chain(user_qset, shift_qset)
#    return chained_qsets
    return User.objects.filter(Q(first_name__icontains=q) | Q(last_name__icontains=q))

  def format_match(self, obj):
    """ (HTML) formatted item for display in the dropdown """
#    if isinstance(obj, Shift):
#      return u'Call: %s' % obj
#    if isinstance(obj, User):
    return u'%s' % obj.get_full_name()
    #return u'%s' % (tag.name)

  def format_item_display(self, obj):
    """ (HTML) formatted item for displaying item in the selected deck area """
#    if isinstance(obj, Shift):
#      return u'Call: %s' % obj
#    if isinstance(obj, User):
    profile_url = reverse('user_profile', kwargs={'username': obj.username})
    return u'<a href="%s" rel="facebox">%s</a>' % (profile_url, obj.get_full_name())
    #return unicode(tag)

  def get_objects(self, ids):
#    return Profile.objects.filter(pk__in=ids).order_by('last_name')
    ids = [int(id) for id in ids]
    things = self.model.objects.in_bulk(ids)
    return [things[aid] for aid in ids if things.has_key(aid)]

  def check_auth(self,request):
      """ to ensure that nobody can get your data via json simply by knowing the URL.
          public facing forms should write a custom LookupChannel to implement as you wish.
          also you could choose to return HttpResponseForbidden("who are you?")
          instead of raising PermissionDenied (401 response)
       """
      if not request.user.is_authenticated():
          raise PermissionDenied