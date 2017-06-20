from django.conf.urls import patterns
from django.conf.urls import url

from openstack_dashboard.dashboards.security.security_overview import views


urlpatterns = patterns(
    'openstack_dashboard.dashboards.security.security_overview.views',
    url(r'^$', views.MainIndexView.as_view(), name='index'),
)