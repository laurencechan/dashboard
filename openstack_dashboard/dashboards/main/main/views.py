# from horizon import tables

# from openstack_dashboard.dashboards.main.main \
#     import tables as project_tables

# class MainIndexView(tables.DataTableView):
#     table_class = project_tables.MainTable
#     template_name = 'main/main/main.html'
#     page_title = "main page"

#     def get_data(self):
#         data = []
#         return data

# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import horizon

from horizon import views

from openstack_dashboard import api

from openstack_dashboard import policy

class MainIndexView(views.APIView):
    template_name = 'main/main/main.html'

    def get_data(self, request, context, *args, **kwargs):
        context["cluster"] = {}
        #import pydevd
        #pydevd.settrace('172.16.6.2', port=60001, stdoutToServer=True, stderrToServer=True)
        hypervisor_stats_count = {}
        #import pydevd
        #pydevd.settrace('172.16.6.2', port=60001, stdoutToServer=True, stderrToServer=True)
        hypervisor_stats_count['down'] = 0
        hypervisor_stats_count['up'] = 0

        instance_stats_count = {}
        instance_stats_count['down'] = 0
        instance_stats_count['up'] = 0
        instance_stats_count['active'] = 0
        instance_stats_count['running'] = 0
        instance_stats_count['idle'] = 0
        instance_stats_count['free'] = 0
        if policy.check((('identity', 'admin_required'),),
                        self.request):
            # TODO get region extra or description
            context["cluster"]["clusters_list"] = request.user.available_services_regions
            context["cluster"]["current_cluster"] = request.user.services_region

            stats = api.nova.hypervisor_stats(self.request)
            context["cluster"]["hypervisor_stats"] = api.nova.hypervisor_stats(self.request)

            hypervisor_list = api.nova.hypervisor_list(self.request)
            for hypervisor in hypervisor_list:
                if hypervisor.state == 'up':
                    hypervisor_stats_count['up'] += 1
                if hypervisor.state == 'down':
                    hypervisor_stats_count['down'] += 1

            # TODO check data and other api
            instance_list = api.nova.server_list(self.request, all_tenants=True)[0]
            for instance in instance_list:
                if instance.status == 'ACTIVE':
                    instance_stats_count['active'] += 1
                    instance_stats_count['up'] += 1
                if instance.status == 'RUNNING':
                    instance_stats_count['running'] += 1
                    instance_stats_count['up'] += 1
                if instance.status == 'SUSPENDED':
                    instance_stats_count['idle'] += 1
                    instance_stats_count['up'] += 1
                if instance.status == 'CRASHED':
                    instance_stats_count['free'] += 1
                    instance_stats_count['up'] += 1
                if instance.status == 'SHUTOFF':
                    instance_stats_count['down'] += 1

        elif policy.check((('identity', 'admin_or_owner'),),self.request):
            # doing
            tenant_id = self.request.user.token.project.get('id')
            # request.user.tenant_id
            tenant_quota = api.nova.tenant_quota_get(self.request, tenant_id)
            one_cluster = { 'vcpus': tenant_quota.get('cores').limit, 'memory_mb': tenant_quota.get('ram').limit / 1024.0, 'local_gb_used': 0, 'local_gb': 0 }
            # vms all count: ttenant_quota.get('instances').limit

            # from django.utils import timezone
            # now = timezone.now()
            # import datetime
            # now = datetime.date.today()
            # start_day = datetime.date(now.year, now.month, 1)
            # start = datetime.datetime(start_day.year, start_day.month,
            #                       start_day.day, 0, 0, 0, 0)
            # end = datetime.datetime(now.year, now.month, now.day, 23, 59, 59, 0)
            # api.nova.usage_get(self.request, self.request.user.token.project.get('id'), start, end)

            context["cluster"]["hypervisor_stats"] = one_cluster
        context["cluster"]["hypervisor_stats_count"] = hypervisor_stats_count
        context["cluster"]["instance_stats_count"] = instance_stats_count
        return context
