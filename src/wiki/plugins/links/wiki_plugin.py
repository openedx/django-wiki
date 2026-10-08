from django.urls import path, reverse_lazy
from django.utils.translation import gettext_lazy as _

from wiki.conf import settings
from wiki.core.plugins import registry
from wiki.core.plugins.base import BasePlugin
from wiki.plugins.links import views
from wiki.plugins.links.mdx.djangowikilinks import WikiPathExtension
from wiki.plugins.links.mdx.urlize import makeExtension


class LinkPlugin(BasePlugin):
    
    slug = 'links'
    urlpatterns = [
        path('json/query-urlpath/', views.QueryUrlPath.as_view(), name='links_query_urlpath'),
    ]
    
    sidebar = {'headline': _('Links'),
               'icon_class': 'icon-bookmark',
               'template': 'wiki/plugins/links/sidebar.html',
               'form_class': None,
               'get_form_kwargs': (lambda a: {})}
    
    wikipath_config = [
        ('base_url', reverse_lazy('wiki:get', kwargs={'path': ''}) ),
        ('live_lookups', settings.LINK_LIVE_LOOKUPS ),
        ('default_level', settings.LINK_DEFAULT_LEVEL ),
        ]
    
    markdown_extensions = [makeExtension(), WikiPathExtension(**dict(wikipath_config))]
    
    def __init__(self):
        pass


registry.register(LinkPlugin)
