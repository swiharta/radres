from models import *
from django.contrib import admin

	
class ProfileAdmin(admin.ModelAdmin):
  list_editable = ('short_range', 'long_range', 'phone', 'email')
  list_display_links = ('username',)
  list_display = ('username', 'first_name', 'last_name', 'grad_year', 'ical', 'short_range', 'long_range', 'phone', 'email')
  search_fields = ('username', 'first_name', 'last_name' ) # 'tags__name',
  list_filter = ('grad_year', 'ical',)
#  date_hierarchy = 'date'
  
admin.site.register(Profile, ProfileAdmin)