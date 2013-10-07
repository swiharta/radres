from django.contrib import admin
# from treebeard.admin import TreeAdmin
from mptt.admin import MPTTModelAdmin

from taxonomy.models import *
	
class SubspecialtyAdmin(admin.ModelAdmin):
	prepopulated_fields = { 'slug': ['name'] }
	list_display = ('name', 'abbr', 'slug', 'id')

admin.site.register(Subspecialty, SubspecialtyAdmin)