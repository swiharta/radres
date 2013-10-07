from models import *
from django.contrib import admin
from adminforms import AnswerForm


class ChoiceInline(admin.TabularInline):
  model = Choice
  extra = 1
  fields = ('letter', 'text',)
  # template = 'cases/admin/choice/edit_inline_tabular.html'

class AnswerInline(admin.TabularInline):
  model = Answer
  extra = 1
  fields = ('choice', 'text', 'user')

  def formfield_for_foreignkey(self, db_field, request=None, **kwargs):

    field = super(AnswerInline, self).formfield_for_foreignkey(db_field, request, **kwargs)

    if db_field.name == 'choice':
      if request._obj_ is not None:
        field.queryset = field.queryset.filter(question = request._obj_)
      else:
        field.queryset = field.queryset.none()

    return field


class QuestionAdmin(admin.ModelAdmin):
  list_editable = ('set', 'div')
  list_display_links = ('id',)
  list_display = ('id', 'set', 'div', 'text', 'modified')
  list_filter = ('div', 'set',)
  search_fields = ('text', 'id')

  inlines = [ChoiceInline, AnswerInline]
  
#  form = AnswerForm
  
  def modified_format(self, obj): # shorten nanosecond precision display
    return obj.modified.strftime('%d %b %Y %H:%M')
  
  modified_format.short_description = 'Modified'
  modified_format.admin_order_field = 'modified'

  def get_form(self, request, obj=None, **kwargs):
    # just save obj reference for future processing in Inline
    request._obj_ = obj
    return super(QuestionAdmin, self).get_form(request, obj, **kwargs)
  
class AnswerAdmin(admin.ModelAdmin):
  list_editable = ('user',)
  list_display_links = ('id',)
  list_display = ('id', 'user', 'choice', 'modified')
  list_filter = ('user',)
  search_fields = ('text', 'id')
  
  def modified_format(self, obj): # shorten nanosecond precision display
    return obj.modified.strftime('%d %b %Y %H:%M')
  
  modified_format.short_description = 'Modified'
  modified_format.admin_order_field = 'modified'
  
  form = AnswerForm

class ChoiceAdmin(admin.ModelAdmin):
#  list_editable = ('letter',)
  list_display_links = ('id',)
  list_display = ('id', 'letter', 'text', 'correct')
#  list_filter = ('question',)
  search_fields = ('text',)

class UserChoiceAdmin(admin.ModelAdmin):
  list_editable = ('mark', 'ignore')
  list_display_links = ('id',)
  list_display = ('id', 'question_id', 'user', 'choice', 'correct', 'mark', 'ignore', 'modified')
  list_filter = ('user', 'mark', 'ignore')
#  search_fields = ('choice',)

  def modified_format(self, obj): # shorten nanosecond precision display
    return obj.modified.strftime('%d %b %Y %H:%M')

  modified_format.short_description = 'Modified'
  modified_format.admin_order_field = 'modified'

  def question_id(self, obj): # shorten nanosecond precision display
    return obj.question.id

  question_id.short_description = 'Question ID'
  question_id.admin_order_field = 'question'
  
admin.site.register(Answer, AnswerAdmin)
admin.site.register(UserChoice, UserChoiceAdmin)
#admin.site.register(UserChoice, admin.ModelAdmin)
admin.site.register(Choice, ChoiceAdmin)
admin.site.register(Question, QuestionAdmin)