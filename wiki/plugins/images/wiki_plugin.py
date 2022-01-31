from django.urls import include, re_path
from django.utils.translation import gettext_lazy as _

from wiki.core.plugins import registry
from wiki.core.plugins.base import BasePlugin
from wiki.plugins.images import views, models, settings, forms
from wiki.plugins.notifications import ARTICLE_EDIT
from wiki.plugins.images.markdown_extensions import ImageExtension


class ImagePlugin(BasePlugin):
    
    slug = settings.SLUG
    sidebar = {
        'headline': _('Images'),
        'icon_class': 'icon-picture',
        'template': 'wiki/plugins/images/sidebar.html',
        'form_class': forms.SidebarForm,
        'get_form_kwargs': (lambda a: {'instance': models.Image(article=a)})
    }
    
    # List of notifications to construct signal handlers for. This
    # is handled inside the notifications plugin.
    notifications = [
        {'model': models.ImageRevision,
         'message': lambda obj: _("An image was added: %s") % obj.get_filename(),
         'key': ARTICLE_EDIT,
         'created': False,
         'ignore': lambda revision: bool(revision.previous_revision), # Ignore if there is a previous revision... the image isn't new
         'get_article': lambda obj: obj.article}
    ]
    
    class RenderMedia:
        js = [
            'wiki/colorbox/colorbox/jquery.colorbox-min.js',
            'wiki/js/images.js',
        ]
        
        css = {
            'screen': 'wiki/colorbox/example1/colorbox.css'
        }

    urlpatterns = [
        re_path('^$', views.ImageView.as_view(), name='images_index'),
        re_path(r'^delete/(?P<image_id>\d+)/$', views.DeleteView.as_view(), name='images_delete'),
        re_path(r'^restore/(?P<image_id>\d+)/$', views.DeleteView.as_view(), name='images_restore', kwargs={'restore': True}),
        re_path(r'^purge/(?P<image_id>\d+)/$', views.PurgeView.as_view(), name='images_purge'),
        re_path(r'^(?P<image_id>\d+)/revision/change/(?P<rev_id>\d+)/$', views.RevisionChangeView.as_view(), name='images_restore'),
        re_path(r'^(?P<image_id>\d+)/revision/add/$', views.RevisionAddView.as_view(), name='images_add_revision'),
    ]

    markdown_extensions = [ImageExtension()]
    
    def __init__(self):
        #print "I WAS LOADED!"
        pass
    
registry.register(ImagePlugin)

