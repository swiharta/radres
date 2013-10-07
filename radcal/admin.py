from models import *
from django.contrib import admin
from datetime import datetime
#from django_monitor.admin import MonitorAdmin
#from moderation.admin import ModerationAdmin

# from adminforms import *
	
#class ShiftEventAdmin(ModerationAdmin):
class ShiftEventAdmin(admin.ModelAdmin):
  list_editable = ('date', 'shift')
  list_display_links = ('resident', 'user')
  list_display = ('date', 'shift', 'resident', 'user', 'modified')
  search_fields = ('resident', 'user' ) # 'tags__name',
  list_filter = ('date', 'modified', 'shift', 'resident' , 'user')
  date_hierarchy = 'date'

  def modified_format(self, obj): # shorten the default nanosecond precision display
    return obj.modified.strftime('%d %b %Y %H:%M')

  def save_model(self, request, obj, form, change):
    if obj.shift and not obj.start:
      obj.start = datetime.combine(obj.date, obj.shift.start_time)
      obj.end = datetime.combine(obj.date, obj.shift.end_time)
    obj.save()

  modified_format.short_description = 'Modified'
  modified_format.admin_order_field = 'modified'

class ShiftAdmin(admin.ModelAdmin):
  list_editable = ('hospital', 'code', 'abbr', 'weekend', 'initials', 'start_time', 'end_time', 'cash', 'night_call', 'day_call')
  list_display_links = ('name',)
  list_display = ('name', 'code', 'abbr', 'initials', 'hospital', 'weekend', 'start_time', 'end_time', 'cash', 'night_call', 'day_call')

class ConferenceAdmin(admin.ModelAdmin):
  list_editable = ('location', 'name', 'abbr', 'start_time', 'end_time')
  list_display_links = ('id',)
  list_display = ('id', 'location', 'name', 'abbr', 'start_time', 'end_time')

class ConfEventAdmin(admin.ModelAdmin):
  list_editable = ('link', 'presenter', 'div', 'title', 'date')
  list_display_links = ('id',)
  list_display = ('id', 'date', 'link', 'title', 'presenter', 'div', 'subspecialty', 'modified')
  list_filter = ('div', 'start', 'public')
  radio_fields = {'conference': admin.VERTICAL}
  search_fields = ('presenter', 'title') # 'tags__name', 
  date_hierarchy = 'start'
  fieldsets = (
    (None, {
      'fields': ('date', 'conference', 'presenter', 'div', 'subspecialty', 'title', 'link',)
    }),
    ('Advanced options', {
      'classes': ('collapse',),
      'fields': ('start', 'end','public','remind',)
    }),
    )
  
  def modified_format(self, obj): # shorten nanosecond precision display
    return obj.modified.strftime('%d %b %Y %H:%M')

  def save_model(self, request, obj, form, change):
    if obj.conference and not obj.start:
      obj.start = datetime.combine(obj.date, obj.conference.start_time)
      obj.end = datetime.combine(obj.date, obj.conference.end_time)
    obj.save()
  
  modified_format.short_description = 'Modified'
  modified_format.admin_order_field = 'modified'  
  
admin.site.register(Shift, ShiftAdmin)
admin.site.register(ShiftEvent, ShiftEventAdmin)
admin.site.register(ConfEvent, ConfEventAdmin)
admin.site.register(Conference, ConferenceAdmin)
admin.site.register(EventFilter, admin.ModelAdmin)
