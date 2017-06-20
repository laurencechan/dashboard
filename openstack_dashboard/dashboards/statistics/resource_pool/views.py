from horizon import tables
from horizon import views

from openstack_dashboard import api

from openstack_dashboard import policy
from openstack_dashboard.dashboards.statistics.resource_pool \
    import tables as project_tables


class MainIndexView(views.APIView):
    # table_class = project_tables.MainTable
    template_name = 'statistics/resource_pool/main.html'

    # page_title = "main page"
    def dic_compose(sele, *keys):
        dict_data = {i: 0 for i in keys}
        return dict_data

    def get_data(self, request, context, *args, **kwargs):
        context["hypervisor_stats_count"] = self.dic_compose("up", "down")
        context["instance_stats_count"] = self.dic_compose("up", "down", "active", "running", "idle", "free")
        if policy.check((('identity', 'admin_required'),),
                        self.request):
            # TODO get region extra or description
            context["clusters_list"] = request.user.available_services_regions
            context["current_cluster"] = request.user.services_region
            # stats = api.nova.hypervisor_stats(self.request)
            context["hypervisor_stats"] = api.nova.hypervisor_stats(self.request)
            hypervisor_list = api.nova.hypervisor_list(self.request)
            for hypervisor in hypervisor_list:
                if hypervisor.state == 'up':
                    context["hypervisor_stats_count"]["up"] += 1
                if hypervisor.state == 'down':
                    context["hypervisor_stats_count"]['down'] += 1

            # TODO check data and other api
            instance_list = api.nova.server_list(self.request, all_tenants=True)[0]
            for instance in instance_list:
                if instance.status == 'ACTIVE':
                    context["instance_stats_count"]['active'] += 1
                    context["instance_stats_count"]['up'] += 1
                if instance.status == 'RUNNING':
                    context["instance_stats_count"]['running'] += 1
                    context["instance_stats_count"]['up'] += 1
                if instance.status == 'SUSPENDED':
                    context["instance_stats_count"]['idle'] += 1
                    context["instance_stats_count"]['up'] += 1
                if instance.status == 'CRASHED':
                    context["instance_stats_count"]['free'] += 1
                    context["instance_stats_count"]['up'] += 1
                if instance.status == 'SHUTOFF':
                    context["instance_stats_count"]['down'] += 1

        elif policy.check((('identity', 'admin_or_owner'),), self.request):
            tenant_id = self.request.user.token.project.get('id')
            tenant_quota = api.nova.tenant_quota_get(self.request, tenant_id)
            one_cluster = {'vcpus': tenant_quota.get('cores').limit,
                           'memory_mb': tenant_quota.get('ram').limit / 1024.0, 'local_gb_used': 0, 'local_gb': 0}
            context["hypervisor_stats"] = one_cluster
        return context
