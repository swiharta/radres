from django.contrib import admin
from polls.models import Question, Choice

class ChoiceInline(admin.StackedInline):
	model = Choice
	extra = 2
	verbose_name_plural = 'Add Choices'
	
	exclude = ('total_votes',)

class QuestionAdmin(admin.ModelAdmin):
	def save_model(self, request, obj, form, change):
		if getattr(obj, 'user', None) is None:
			obj.user = request.user
		obj.save()

	list_display = ('id', 'text', 'slug', 'created_on', 'user')
	list_display_links = ('id',)
	prepopulated_fields = { 'slug': ['text'] }
	
	fieldsets = (
		(None, {
			'fields': (('slug', 'user', 'allow_multiple', 'active'),),
		}),
		(None, {
			'fields': (('text'),),
		}),
	)
	
	inlines = [ChoiceInline]
	pass

class ChoiceAdmin(admin.ModelAdmin):
	list_display = ('id', 'question', 'text', 'total_votes')
	list_display_links = ('id',)
	pass

admin.site.register(Question, QuestionAdmin)
admin.site.register(Choice, ChoiceAdmin)