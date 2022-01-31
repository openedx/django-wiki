from django.urls import include, re_path
from django.utils.translation import gettext_lazy as _

from wiki.core.plugins import registry
from wiki.core.plugins.base import BasePlugin
from wiki.plugins.attachments import models, settings, views
from wiki.plugins.attachments.markdown_extensions import AttachmentExtension
from wiki.plugins.notifications import ARTICLE_EDIT


class AttachmentPlugin(BasePlugin):
    
    #settings_form = 'wiki.plugins.notifications.forms.SubscriptionForm'
    
    slug = settings.SLUG
    urlpatterns = [
        re_path(r'^$', views.AttachmentView.as_view(), name='attachments_index'),
        re_path(r'^search/$', views.AttachmentSearchView.as_view(), name='attachments_search'),
        re_path(r'^add/(?P<attachment_id>\d+)/$', views.AttachmentAddView.as_view(), name='attachments_add'),
        re_path(r'^replace/(?P<attachment_id>\d+)/$', views.AttachmentReplaceView.as_view(), name='attachments_replace'),
        re_path(r'^history/(?P<attachment_id>\d+)/$', views.AttachmentHistoryView.as_view(), name='attachments_history'),
        re_path(r'^download/(?P<attachment_id>\d+)/$', views.AttachmentDownloadView.as_view(), name='attachments_download'),
        re_path(r'^delete/(?P<attachment_id>\d+)/$', views.AttachmentDeleteView.as_view(), name='attachments_delete'),
        re_path(r'^download/(?P<attachment_id>\d+)/revision/(?P<revision_id>\d+)/$', views.AttachmentDownloadView.as_view(), name='attachments_download'),
        re_path(r'^change/(?P<attachment_id>\d+)/revision/(?P<revision_id>\d+)/$', views.AttachmentChangeRevisionView.as_view(), name='attachments_revision_change'),
    ]
    
    article_tab = (_('Attachments'), "icon-file")
    article_view = views.AttachmentView().dispatch
    
    # List of notifications to construct signal handlers for. This
    # is handled inside the notifications plugin.
    notifications = [{'model': models.AttachmentRevision,
                      'message': lambda obj: (_("A file was changed: %s") if not obj.deleted else _("A file was deleted: %s")) % obj.get_filename(),
                      'key': ARTICLE_EDIT,
                      'created': True,
                      'get_article': lambda obj: obj.attachment.article}
                     ]
    
    markdown_extensions = [AttachmentExtension()]
    
    def __init__(self):
        #print "I WAS LOADED!"
        pass
    
registry.register(AttachmentPlugin)
