
from django.urls import path
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
        path('', views.AttachmentView.as_view(), name='attachments_index'),
        path('search/', views.AttachmentSearchView.as_view(), name='attachments_search'),
        path('add/<int:attachment_id>/', views.AttachmentAddView.as_view(), name='attachments_add'),
        path('replace/<int:attachment_id>/', views.AttachmentReplaceView.as_view(), name='attachments_replace'),
        path('history/<int:attachment_id>/', views.AttachmentHistoryView.as_view(), name='attachments_history'),
        path('download/<int:attachment_id>/', views.AttachmentDownloadView.as_view(), name='attachments_download'),
        path('delete/<int:attachment_id>/', views.AttachmentDeleteView.as_view(), name='attachments_delete'),
        path('download/<int:attachment_id>/revision/<int:revision_id>/', views.AttachmentDownloadView.as_view(), name='attachments_download'),
        path('change/<int:attachment_id>/revision/<int:revision_id>/', views.AttachmentChangeRevisionView.as_view(), name='attachments_revision_change'),
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
