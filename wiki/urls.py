from django.urls import include, path, re_path

from wiki.conf import settings
from wiki.core.plugins import registry
from wiki.views import accounts, article

urlpatterns = [
    path('', article.ArticleView.as_view(), name='root', kwargs={'path': ''}),
    path('create-root/', article.CreateRootView.as_view(), name='root_create'),
    path('_revision/diff/<int:revision_id>/', article.diff, name='diff'),
]

if settings.ACCOUNT_HANDLING:
    urlpatterns += [
        path('_accounts/sign-up/', accounts.Signup.as_view(), name='signup'),
        path('_accounts/logout/', accounts.Logout.as_view(), name='logout'),
        path('_accounts/login/', accounts.Login.as_view(), name='login'),
    ]

urlpatterns += [
    # This one doesn't work because it don't know where to redirect after...
    path('_revision/change/<int:article_id>/<int:revision_id>/', article.change_revision,
        name='change_revision'),
    path('_revision/preview/<int:article_id>/', article.Preview.as_view(), name='preview_revision'),
    path('_revision/merge/<int:article_id>/<int:revision_id>/preview/', article.merge,
        name='merge_revision_preview', kwargs={'preview': True}),

    # Paths decided by article_ids
    path('<int:article_id>/', article.ArticleView.as_view(), name='get'),
    path('<int:article_id>/delete/', article.Delete.as_view(), name='delete'),
    path('<int:article_id>/deleted/', article.Deleted.as_view(), name='deleted'),
    path('<int:article_id>/edit/', article.Edit.as_view(), name='edit'),
    path('<int:article_id>/preview/', article.Preview.as_view(), name='preview'),
    path('<int:article_id>/history/', article.History.as_view(), name='history'),
    path('<int:article_id>/settings/', article.Settings.as_view(), name='settings'),
    path('<int:article_id>/source/', article.Source.as_view(), name='source'),
    path('<int:article_id>/revision/change/<int:revision_id>/', article.change_revision,
        name='change_revision'),
    path('<int:article_id>/revision/merge/<int:revision_id>/', article.merge, name='merge_revision'),
    re_path(r'^(?P<article_id>\d+)/plugin/(?P<slug>\w+)/$', article.Plugin.as_view(), name='plugin'),
]

for plugin in registry.get_plugins().values():
    slug = getattr(plugin, 'slug', None)
    plugin_urlpatterns = getattr(plugin, 'urlpatterns', None)
    if slug and plugin_urlpatterns:
        urlpatterns += [
            re_path(r'^(?P<article_id>\d+)/plugin/' + slug + '/', include(plugin_urlpatterns)),
            re_path(r'^(?P<path>.+/|)_plugin/' + slug + '/', include(plugin_urlpatterns)),
        ]

urlpatterns += [
    # Paths decided by URLs
    re_path(r'^(?P<path>.+/|)_create/$', article.Create.as_view(), name='create'),
    re_path(r'^(?P<path>.+/|)_delete/$', article.Delete.as_view(), name='delete'),
    re_path(r'^(?P<path>.+/|)_deleted/$', article.Deleted.as_view(), name='deleted'),
    re_path(r'^(?P<path>.+/|)_edit/$', article.Edit.as_view(), name='edit'),
    re_path(r'^(?P<path>.+/|)_preview/$', article.Preview.as_view(), name='preview'),
    re_path(r'^(?P<path>.+/|)_history/$', article.History.as_view(), name='history'),
    re_path(r'^(?P<path>.+/|)_dir/$', article.Dir.as_view(), name='dir'),
    re_path(r'^(?P<path>.+/|)_settings/$', article.Settings.as_view(), name='settings'),
    re_path(r'^(?P<path>.+/|)_source/$', article.Source.as_view(), name='source'),
    re_path(r'^(?P<path>.+/|)_revision/change/(?P<revision_id>\d+)/$', article.change_revision, name='change_revision'),
    re_path(r'^(?P<path>.+/|)_revision/merge/(?P<revision_id>\d+)/$', article.merge, name='merge_revision'),
    re_path(r'^(?P<path>.+/|)_plugin/(?P<slug>\w+)/$', article.Plugin.as_view(), name='plugin'),
    re_path(r'^(?P<path>.+/|)$', article.ArticleView.as_view(), name='get'),
]

app_name = 'wiki'

def get_pattern(app_name="wiki"):
    """Every url resolution takes place as "wiki:view_name".
       You should not attempt to have multiple deployments of the wiki in a
       single Django project.
       https://docs.djangoproject.com/en/dev/topics/http/urls/#topics-http-reversing-url-namespaces
    """
    return urlpatterns, app_name