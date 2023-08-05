from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class NotifcationsConfig(AppConfig):
    name = 'wiki.plugins.notifications'
    verbose_name = _("Wiki notifications")
    label = 'wiki_notifications'


class ImagesConfig(AppConfig):
    name = 'wiki.plugins.images'
    verbose_name = _("Wiki images")
    label = 'wiki_images'


class AttachmentsConfig(AppConfig):
    name = 'wiki.plugins.attachments'
    verbose_name = _("Wiki attachments")
    label = 'wiki_attachments'


class HelpConfig(AppConfig):
    name = "wiki.plugins.help"
    verbose_name = _("Wiki help")
    label = "wiki_help"


class LinksConfig(AppConfig):
    name = "wiki.plugins.links"
    verbose_name = _("Wiki links")
    label = "wiki_links"