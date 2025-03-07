
from django.utils.translation import gettext_lazy as _

from wiki.core.plugins import registry
from wiki.core.plugins.base import BasePlugin


class HelpPlugin(BasePlugin):
    
    slug = 'help'
    urlpatterns = []
    
    sidebar = {'headline': _('Help'),
               'icon_class': 'icon-question-sign',
               'template': 'wiki/plugins/help/sidebar.html',
               'form_class': None,
               'get_form_kwargs': (lambda a: {})}
    
    markdown_extensions = []
    
    def __init__(self):
        pass


registry.register(HelpPlugin)
