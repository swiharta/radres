from django.forms import ModelForm
from django.contrib.auth.models import User
from models import Answer, Choice

class AnswerForm(ModelForm):
	def __init__(self, *args, **kwargs):
		super(AnswerForm, self).__init__(*args, **kwargs)
		# sort ForeignKey drop-downs alphabetically (default is the db order)
		if self.instance:
			self.fields['choice'].queryset = Choice.objects.filter(question=self.instance.question).order_by('letter')		
		if self.instance:
			self.fields['user'].queryset = \
				User.objects.all().order_by('username')
	
	class Meta:
		model = Answer