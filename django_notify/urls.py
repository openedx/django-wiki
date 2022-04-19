from django.urls import path, re_path

from django_notify import views

urlpatterns = [
    path('json/get/', views.get_notifications, name='json_get', kwargs={}),
    path('json/mark-read/', views.mark_read, name='json_mark_read_base', kwargs={}),
    re_path(r'^json/mark-read/(\d+)/$', views.mark_read, name='json_mark_read', kwargs={}),
    path('goto/<int:notification_id>/', views.goto, name='goto', kwargs={}),
    path('goto/', views.goto, name='goto_base', kwargs={}),
]

app_name = 'notify'

def get_pattern(app_name="notify"):
    """Every url resolution takes place as "notify:view_name".
       https://docs.djangoproject.com/en/dev/topics/http/urls/#topics-http-reversing-url-namespaces
    """
    return urlpatterns, app_name