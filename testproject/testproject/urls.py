from django.conf import settings
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path, re_path
from django.views.static import serve as static_serve

admin.autodiscover()

urlpatterns = [
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', static_serve, {'document_root': settings.MEDIA_ROOT}),
    ]


from django_notify.urls import get_pattern as get_notify_pattern
from wiki.urls import get_pattern as get_wiki_pattern

urlpatterns += [
    path('notify/', include('django_notify.urls', namespace='notify')),
    path('', include('wiki.urls', namespace='wiki')),
]
