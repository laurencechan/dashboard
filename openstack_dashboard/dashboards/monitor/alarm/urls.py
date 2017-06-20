from django.conf.urls import patterns
from django.conf.urls import url

from openstack_dashboard.dashboards.monitor.alarm import views


urlpatterns = patterns(
    'openstack_dashboard.dashboards.monitor.alarm.views',
    url(r'^$', views.MainIndexView.as_view(), name='index'),
)