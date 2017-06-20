from django.conf.urls import patterns
from django.conf.urls import url

from openstack_dashboard.dashboards.statistics.vm_run import views


urlpatterns = patterns(
    'openstack_dashboard.dashboards.statistics.vm_run.views',
    url(r'^$', views.MainIndexView.as_view(), name='index'),
)