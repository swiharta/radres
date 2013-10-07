from django.views.generic.base import TemplateView
import os#, glob

class MRIView(TemplateView):
  template_name = "mri/mri_html_listing.html"
  html_dir = os.path.join(os.path.dirname(__file__), 'templates')
  dir_list=os.listdir(html_dir)
  filenames = [filename.split('.')[0] for filename in dir_list if os.path.isfile(os.path.join(html_dir, filename))]

  # filenames = glob.glob(html_dir+"/*.html")

  def get_context_data(self, **kwargs):
    ctx = { "filenames": self.filenames, }
    ctx.update(super(MRIView, self).get_context_data(**kwargs))
    return ctx