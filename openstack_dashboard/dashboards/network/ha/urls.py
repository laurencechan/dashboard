from django.conf.urls import patterns
from django.conf.urls import url

from openstack_dashboard.dashboards.network.ha import views


urlpatterns = patterns(
    'openstack_dashboard.dashboards.network.ha.views',
    url(r'^$', views.MainIndexView.as_view(), name='index'),
)