from django.urls import include, re_path
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.static import serve as static_serve

from django.contrib import admin
admin.autodiscover()

urlpatterns = [
    re_path(r'^admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', static_serve, {'document_root': settings.MEDIA_ROOT}),
    ]


from wiki.urls import get_pattern as get_wiki_pattern
from django_notify.urls import get_pattern as get_notify_pattern

urlpatterns += [
    re_path(r'^notify/', include('django_notify.urls', namespace='notify')),
    re_path(r'', include('wiki.urls', namespace='wiki')),
]
