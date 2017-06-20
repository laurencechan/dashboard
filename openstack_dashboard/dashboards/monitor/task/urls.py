from django.conf.urls import patterns
from django.conf.urls import url

from openstack_dashboard.dashboards.monitor.task import views


urlpatterns = patterns(
    'openstack_dashboard.dashboards.monitor.task.views',
    url(r'^$', views.MainIndexView.as_view(), name='index'),
)