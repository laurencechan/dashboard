# -*- coding: utf-8 -*-
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
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
import logging
import time
import datetime

import horizon
from horizon import views
from horizon import exceptions
from openstack_dashboard import api
from openstack_dashboard import policy
from openstack_dashboard.api import ceilometer

LOG = logging.getLogger(__name__)

class MainIndexView(views.APIView):
    template_name = 'main/main/main.html'

    def init_data(*keys):
        dict_data = {}
        for k in keys:
            dict_data[k] = 0
        return dict_data

    def instance_stats_count(self, start_utc, end_utc):
        instance_stats_count = self.init_data('down', 'up', 'active', 'running', 'idle', 'free')
        instancestates = ceilometer.instancestates(self.request, start_utc, end_utc)
        for instancestate in instancestates:
            status = instancestate['state']
            if status == 'busy':
                instance_stats_count['active'] += 1
                instance_stats_count['up'] += 1
            if status == 'normal':
                instance_stats_count['running'] += 1
                instance_stats_count['up'] += 1
            if status == 'suspended':
                instance_stats_count['idle'] += 1
                instance_stats_count['up'] += 1
            if status == 'idle':
                instance_stats_count['free'] += 1
                instance_stats_count['up'] += 1
            if status == 'stop':
                instance_stats_count['down'] += 1
        return instance_stats_count

    def compute_hosts(self, all_hosts):
        hosts = all_hosts
        for key in hosts.keys():
            if not hosts[key].has_key('nova-compute'):
                hosts.pop(key)
        return hosts

    def cluster_list(self, cluster_list, period, region, hypervisor_list):
        availability_zone = api.nova.availability_zone_list(self.request, detailed=True)
        for zone in availability_zone:
            hosts = self.compute_hosts(zone.hosts) # 计算节点过滤
            
            # 单可用域的计算节点值总汇
            if hosts:
                hypervisor_stats = self.init_data('count', 'running_vms', 'vcpus', 'vcpus_used', 'memory_mb', 'memory_mb_used', 'local_gb', 'local_gb_used')
                hypervisor_stats['region'] = region
                hypervisor_stats['name'] = zone.zoneName
                hypervisor_stats['count'] = len(hosts.keys())
                hypervisor_stats['vcpus_used_ratio'] = round(ceilometer.single_statistic(self.request, 'hardware.cpu.util', None, period, (',').join(hosts.keys())), 3)
                hypervisor_stats['memory_used_ratio'] = round(ceilometer.single_statistic(self.request, 'hardware.memory.util', None, period, (',').join(hosts.keys())), 3)

                for hypervisor in hypervisor_list:
                    if hypervisor.hypervisor_hostname in hosts.keys():
                        hypervisor_stats['running_vms'] += hypervisor.running_vms
                        hypervisor_stats['vcpus'] += hypervisor.vcpus
                        hypervisor_stats['vcpus_used'] += hypervisor.vcpus_used
                        hypervisor_stats['memory_mb'] += hypervisor.memory_mb
                        hypervisor_stats['memory_mb_used'] += hypervisor.memory_mb_used
                        hypervisor_stats['local_gb'] += hypervisor.local_gb
                        hypervisor_stats['local_gb_used'] += hypervisor.local_gb_used
                cluster_list.append(hypervisor_stats)
        return cluster_list

    def hypervisor_stats_count(self, hypervisor_list):
        hypervisor_stats_count = self.init_data('down', 'up')
        for hypervisor in hypervisor_list:
            if hypervisor.state == 'up':
                hypervisor_stats_count['up'] += 1
            if hypervisor.state == 'down':
                hypervisor_stats_count['down'] += 1
        return hypervisor_stats_count

    def get_data(self, request, context, *args, **kwargs):
        # 数据初始化
        context["regions_detail_data"] = {}
        context["hypervisor_stats"] = self.init_data('count', 'running_vms', 'vcpus', 'vcpus_used', 'memory_mb', 'memory_mb_used', 'local_gb', 'local_gb_used')
        context['hypervisor_stats_count'] = self.init_data('down', 'up')
        cluster_list = []
        context["instance_stats_count"] = self.init_data('down', 'up', 'active', 'running', 'idle', 'free')
        context["data_centers"] = getattr(settings, 'DATA_CENTERS', {})

        # 当月时间段
        end = time.time()
        start_str = "%s-%s-01" % (time.localtime(end).tm_year, time.localtime(end).tm_mon)
        start  = time.mktime(time.strptime(start_str, "%Y-%m-%d"))
        end_utc = datetime.datetime.utcfromtimestamp(end).strftime("%Y-%m-%dT%H:%M:%S")
        start_utc = datetime.datetime.utcfromtimestamp(start).strftime("%Y-%m-%dT%H:%M:%S")

        if policy.check((('identity', 'admin_required'),),
                        self.request):
            # 多 region 信息
            context['page_url'] = request.horizon.get('panel').get_absolute_url()
            multi_data_centers = getattr(settings, 'MULTI_DATA_CENTERS', False)
            context['multi_data_centers'] = multi_data_centers
            regions_list = request.user.available_services_regions if multi_data_centers else [request.user.services_region]
            context["regions_list"] = regions_list
            context["current_region"] = request.user.services_region
            context["default_option"] = request.user.services_region

            # region 切换选择
            request_region = request.GET.get('region')
            regions = regions_list
            if request_region in regions_list:
                regions = [request_region]
                context["default_option"] = request_region

            # 多 region 数量总汇
            for region in regions:
                try:
                    request.user.services_region = region

                    # 计算主机参数详情
                    region_hypervisor_stats = self.init_data('count', 'running_vms', 'vcpus', 'vcpus_used', 'memory_mb', 'memory_mb_used', 'local_gb', 'local_gb_used')
                    region_hypervisor_stats = api.nova.hypervisor_stats(self.request)
                    context["hypervisor_stats"]['count'] += region_hypervisor_stats.count
                    context["hypervisor_stats"]['running_vms'] += region_hypervisor_stats.running_vms
                    context["hypervisor_stats"]['vcpus'] += region_hypervisor_stats.vcpus
                    context["hypervisor_stats"]['vcpus_used'] += region_hypervisor_stats.vcpus_used
                    context["hypervisor_stats"]['memory_mb'] += region_hypervisor_stats.memory_mb
                    context["hypervisor_stats"]['memory_mb_used'] += region_hypervisor_stats.memory_mb_used
                    context["hypervisor_stats"]['local_gb'] += region_hypervisor_stats.local_gb
                    context["hypervisor_stats"]['local_gb_used'] += region_hypervisor_stats.local_gb_used

                    hypervisor_list = api.nova.hypervisor_list(self.request)

                    # 计算主机状态数量
                    hypervisor_stats_count = self.hypervisor_stats_count(hypervisor_list)
                    context['hypervisor_stats_count']['up'] += hypervisor_stats_count['up']
                    context['hypervisor_stats_count']['down'] += hypervisor_stats_count['down']

                    # 集群列表集
                    cluster_list = self.cluster_list(cluster_list, int(end - start), region, hypervisor_list)

                    # 虚拟机状态数量
                    instance_stats_count = self.instance_stats_count(start_utc, end_utc)
                    context["instance_stats_count"]['down'] += instance_stats_count['down'] #关机
                    context["instance_stats_count"]['up'] += instance_stats_count['up'] #启动
                    context["instance_stats_count"]['active'] += instance_stats_count['active'] #繁忙
                    context["instance_stats_count"]['running'] += instance_stats_count['running'] #正常
                    context["instance_stats_count"]['idle'] += instance_stats_count['idle'] #空置
                    context["instance_stats_count"]['free'] += instance_stats_count['free'] #空闲
                except Exception as e:
                    LOG.debug('Main homepage failed in %s: %s', region, e)
                    exceptions.handle(self.request,
                              _('Something Error In %s.' % region))

            if multi_data_centers:
                request.user.services_region = context["current_region"]

        context["cluster_list"] = cluster_list
        return context
