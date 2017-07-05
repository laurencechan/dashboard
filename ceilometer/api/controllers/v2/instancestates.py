
import datetime
from six.moves import urllib
from oslo_utils import timeutils
import pecan
from pecan import rest
import six
from wsme import types as wtypes
import wsmeext.pecan as wsme_pecan
import wsme
from ceilometer.api.controllers.v2 import base
from ceilometer.api.controllers.v2 import utils as ins_utils
from ceilometer.api.controllers.v2 import meters
from ceilometer.api import rbac
from ceilometer.i18n import _
from ceilometer.compute import virt
from ceilometer import nova_client as nova_cli
from ceilometer import sample
from ceilometer import storage
from ceilometer import utils
import samples
class instancestates(base.Base):
    instance_id = wtypes.text
    state=wtypes.text
    @classmethod
    def format(cls,m):
            return cls(
                instance_id=m['instance_id'],
                state=m['state']
            )

class projectwithvmstate(base.Base):
    project_id=wtypes.text
    busy_state=int
    idle_state=int
    suspended_state=int
    normal_state=int
    stop_state=int
    @classmethod
    def format(cls,m):
        return cls(
            project_id=m['project_id'],
            busy_state=m['busy'],
            idle_state = m['idle'],
            suspended_state = m['suspended'],
            normal_state = m['normal'],
            stop_state = m['stop']
        )
class vmstatisticsinfo(base.Base):
    instance_id = wtypes.text
    instance_name = wtypes.text
    state = wtypes.text
    ip = wtypes.text
    cluster = wtypes.text
    flavor={wtypes.text:int}
    cpu_range = {wtypes.text: float}
    cpu_util_range = {wtypes.text: float}
    memory_range = {wtypes.text: float}
    memory_util_range = {wtypes.text: float}
    os_type=wtypes.text

    @classmethod
    def format(cls, m):
        return cls(
            instance_id=m['instance_id'],
            instance_name=m['instance_name'],
            state=m['state'],
            ip=m['ip'],
            cluster=m['cluster'],
            flavor=m['flavor'],
            cpu_range=m['cpu_range'],
            cpu_util_range=m['cpu_util'],
            memory_range=m['memory_range'],
            memory_util_range=m['memory_util'],
            os_type=m['os_type']
        )
class instance_help_base(object):
    _states = ("busy", "idle", "stop", "suspended", "normal")
    _state_suspend_range = {'cpu': 1, 'diskIO': 20, 'networkIO': 1}
    _state_area_cal_args = [{'busy': {'min': 70, 'max': 100}},
                            {'idle': {'min': 0, 'max': 30}}]
    _disk_network_rate = ('disk.write.bytes.rate', 'disk.read.bytes.rate', 'network.outgoing.bytes.rate',
                          'network.incoming.bytes.rate')
    def __init__(self,timeStart,timeEnd):
        self.nova_cli=nova_cli.Client()
        self.instances={}
        self.timeStart=timeStart
        self.timeEnd=timeEnd
    def _get_all_instances_without_deleted(self,endtime):
        try:
            instances=self.nova_cli.instance_get_deleted_in_timestamp(endtime)
        except Exception:
            return []
        for instance in instances:
            if getattr(instance, 'OS-EXT-STS:vm_state', None) in ['deleted',
                                                                  'error','building']:
                continue
       	    else:
                self.instances[instance.id] = instance
        return self.instances.values()

    class time_info(object):
        def __init__(self, time, action):
            self.time = time
            self.action = action
    
    class flavor(object):
        def __init__(self,id):
            self.id=id
    
    def Get_Flavor_Info(self,flavor_id):
        flavor_obj=self.flavor(flavor_id)
        try:
            flavor_info=self.nova_cli.flavor_get_by_id(flavor_obj)
        except:
            raise base.ClientSideError(_("the flavor is not found,id is %s")%flavor_id)
        return  flavor_info

    def get_all_instance_in_timestamp(self):
        try:
            instances_deleted=self.nova_cli.instance_get_deleted_in_timestamp(self.timeEnd)
        except:
            return []
        try:
            instances_not_deleted=self.nova_cli.instance_get_not_deleted_in_timestamp(self.timeEnd)
        except:
            return []
        for instance in instances_deleted:
            if getattr(instance, 'OS-EXT-STS:vm_state', None) in ['building','error']:
                continue
            else:
                self.instances[instance.id]=instance
        for instance in instances_not_deleted:
            if getattr(instance, 'OS-EXT-STS:vm_state', None) in ['building','error']:
                continue
            else:
                self.instances[instance.id] = instance
        return  self.instances.values()

        # Get the really boot time
    def Get_real_timestamp(self, instance):
            timeS = timeutils.parse_isotime(self.timeStart)
            timeE = timeutils.parse_isotime(self.timeEnd)
            timeC = getattr(instance, 'created', None)
            if timeC is None:
                raise base.ClientSideError(_("the instance create time is None"))
            else:
                timeC = timeutils.parse_isotime(timeC)
                time1 = self.compare_timestamp(timeS, timeC)
                time2 = self.compare_timestamp(timeE, timeC)
                if time2 == timeC:
                    return 0
                timeS = timeutils.isotime(time1)
                timeE = timeutils.isotime(time2)
                return self.Get_Time_interval(timeS, timeE)

    def Get_Time_interval(self, timeStart, timeEnd):
            interval_date = timeutils.parse_isotime(timeEnd) - timeutils.parse_isotime(timeStart)
            interval = interval_date.seconds + (interval_date.days * 24 * 60 * 60)
            return interval

    def get_instance_boot_time(self, instance, timeStart, timeEnd):
            try:
                boot_time = 0.0
                instance_actions = self.nova_cli.server_action_get_all(instance)
                if len(instance_actions) == 0:
                    return boot_time
                if len(instance_actions) == 1:
                    return boot_time
                timeStart = timeutils.parse_isotime(timeStart).replace(tzinfo=None)
                timeEnd = timeutils.parse_isotime(timeEnd).replace(tzinfo=None)
                time_list = []
                time_list.append(self.time_info(timeStart, 'query_s'))
                time_list.append(self.time_info(timeEnd, 'query_e'))
                for action in instance_actions:
                    time = timeutils.parse_isotime(action.start_time).replace(tzinfo=None)
                    time_list.append(self.time_info(time, action.action))
                new_time_l = sorted(time_list, key=lambda time: time.time)
                start_index = 0
                end_index = 0
                i = 0
                for time in new_time_l:
                    if time.action == 'query_s':
                        start_index = i
                    elif time.action == 'query_e':
                        end_index = i
                    i += 1
                index = start_index
                while index < end_index:
                    if new_time_l[index + 1].action == 'stop':
                        boot_time += (new_time_l[index + 1].time - new_time_l[index].time).seconds
                    index += 1
                if new_time_l[end_index - 1].action == 'start' \
                        or new_time_l[end_index - 1].action == 'reboot':
                    boot_time += (new_time_l[end_index].time - new_time_l[end_index - 1].time).seconds
                return boot_time
            except Exception:
                boot_time = 0.0
                return boot_time

    def compare_timestamp(self, time1, time2):
            if time1 >= time2:
                return time1
            else:
                return time2

                # get the query object

    def set_Query(self, field, op, value, type):
            query = base.Query()
            query.field = field
            query.op = op
            query.value = value
            query.type = type
            return query

         # make the sample query filter

    def sample_query(self, start_time, end_time,resource_id=None):
            q = []
            query1 = self.set_Query('timestamp', 'gt', start_time, 'datetime')
            q.append(query1)
            query2 = self.set_Query('timestamp', 'lt', end_time, 'datetime')
            q.append(query2)
            if resource_id is not None:
                query3=self.set_Query('resource_id','eq',resource_id,'string')
                q.append(query3)
            return q

        # get statistic of meter

    def statistics_meter(self, instance_id, timeStart, timeEnd, meter_type):
            q = []
            resource_query = self.set_Query('resource_id', 'eq', instance_id, 'string')
            q.append(resource_query)
            timeS_query = self.set_Query('timestamp', 'gt', timeStart, 'datetime')
            q.append(timeS_query)
            timeE_query = self.set_Query('timestamp', 'lt', timeEnd, 'datetime')
            q.append(timeE_query)
            kwargs = ins_utils.query_to_kwargs(q, storage.SampleFilter.__init__)
            kwargs['meter'] = meter_type
            groupby = []
            aggregate = []
            filter = storage.SampleFilter(**kwargs)
            group = meters._validate_groupby_fields(groupby)
            aggregate = utils.uniq(aggregate, ['func', 'param'])
            duration = self.Get_Time_interval(timeStart, timeEnd) * 3600
            statistic_info = pecan.request.storage_conn.get_meter_statistics(
                filter, duration, group, aggregate)
            timeStart = timeutils.parse_isotime(timeStart).replace(tzinfo=None)
            timeEnd = timeutils.parse_isotime(timeEnd).replace(tzinfo=None)
            statistic = [meters.Statistics(start_timestamp=timeStart,
                                           end_timestamp=timeEnd,
                                           **c.as_dict())
                         for c in statistic_info]
            return statistic

    def Get_Cpu_Util_Info(self, timeStart, timeEnd, instance_id):
        cpu_util_info = self.statistics_meter(instance_id, timeStart, timeEnd, 'cpu_util')
        if len(cpu_util_info) == 0:
            return {'max': 0, 'avg': 0, 'min': 0}
        cpu_info_dict = {'max': cpu_util_info[-1].max, 'min': cpu_util_info[-1].min, 'avg': cpu_util_info[-1].avg}
        return cpu_info_dict

    #get the rate of memory_util:(avg,max,min)
    def Get_Memory_Util_Info(self,timeStart,timeEnd,instance_id,total_memory):
        mem_util_info=self.statistics_meter(instance_id,timeStart,timeEnd,'memory.usage')
	if len(mem_util_info) == 0 :
            return {'max':0,'avg':0,'min':0}
        mem_util_avg=(mem_util_info[-1].avg/total_memory )*100
        mem_util_max=(mem_util_info[-1].max/total_memory)*100
        mem_util_min=(mem_util_info[-1].min/total_memory)*100
        mem_info_dict={'max':mem_util_max,'min':mem_util_min,'avg':mem_util_avg}
        return mem_info_dict

    def Get_IO_Avg_Rate(self, timeStart, timeEnd, instance_id):
        rate_list = []
        for meter_value in self._disk_network_rate:
            avg_rate = self.statistics_meter(instance_id, timeStart, timeEnd, meter_value)
            if len(avg_rate) == 0:
                rate_list.append(0.0)
            else:
                rate_list.append(avg_rate[-1].avg)
        return rate_list

    # get the sample from db by filter with query
    def sample_operation(self, q=None, limit=None):
            q = q or {}
            kwargs = ins_utils.query_to_kwargs(q, storage.SampleFilter.__init__)
            f = storage.SampleFilter(**kwargs)
            return map(samples.Sample.from_db_model,
                       pecan.request.storage_conn.get_samples(f, limit=limit))

    # get the instance data from samples which are selecting from db

    def get_instance_sample(self, instance_id, args):
            instance_sample = []
            for arg in args:
                if arg.resource_id == instance_id:
                    instance_sample.append(arg)
            return instance_sample
    def get_util_from_sample(self,memery_total,args):
        cpu_util=[]
        memery_util=[]
        for arg in args:
            if arg.meter=='cpu_util':
                cpu_util.append(arg.volume)

            elif arg.meter=='memory.usage':
                mem_rate=(arg.volume/memery_total)*100
                memery_util.append(mem_rate)
        return dict(cpu_util=cpu_util,memory_util=memery_util)

    def rate_cal(self,util):
        if len(util) == 0:
            return dict(busy=0.0,idle=0.0,normal=0.0)
        busy_count = 0.0
        idl_count = 0.0
        normal_count = 0.0
        state_range_busy=self._state_area_cal_args[0]['busy']
        state_range_idle=self._state_area_cal_args[1]['idle']
        for cr in util:
            state=float(cr)
            if state >= state_range_busy['min'] and state <=state_range_busy['max']:
                busy_count += 1
            elif state >= state_range_idle['min'] and state <=state_range_idle['min']:
                idl_count += 1
            else:
                normal_count += 1
        avg_sum=busy_count+normal_count+idl_count
        busy_rate = (busy_count / avg_sum) * 100
        idl_rate = (idl_count / avg_sum) * 100
        normal_rate = (normal_count / avg_sum) * 100
        return dict(busy=busy_rate,idle=idl_rate,normal=normal_rate)

    # check the instance state is suspended
    def Is_suspended_state(self, timeS, timeE, instance_id, cpu_rate):
            state_range = self._state_suspend_range
            if cpu_rate['avg'] >= state_range['cpu']:
                return False
            rate_list = self.Get_IO_Avg_Rate(timeS, timeE, instance_id)
            if rate_list[0] >= (state_range['diskIO'] * 1024) \
                    or rate_list[1] >= (state_range['diskIO'] * 1024):
                return False
            if rate_list[2] >= (state_range['networkIO'] * 1024) \
                    or rate_list[3] >= (state_range['networkIO'] * 1024):
                return False
            return True
    def format_instance(self,obj,state,**kwargs):
        pass

    def calculate_state(self,instance,**kwargs):
        pass

class state_help(instance_help_base):
    def __init__(self,timeStart,timeEnd):
        super(state_help, self).__init__(timeStart,timeEnd)
    def calculate_state(self,instance,**kwargs):
        info_dict = kwargs['kwargs']
        cpu_rate = info_dict['cpu_util']
        memery_rate = info_dict['memery_util']
        if cpu_rate['busy'] > 10 or memery_rate['busy'] > 10:
            state = 'busy'
        elif cpu_rate['idle'] > 95 or memery_rate['idle'] > 95:
            state = 'idle'
        else:
            state = 'normal'
        instancestates = self.format_instance(instance,state)
        return instancestates
    def format_instance(self,obj,state,**kwargs):
        state_info={}
        state_info['instance_id']=obj.id
        state_info['state']=state
        return state_info

class vm_statistic_help(instance_help_base):
    def __init__(self,timeStart,timeEnd):
        super(vm_statistic_help, self).__init__(timeStart,timeEnd)
    def calculate_state(self,instance,**kwargs):
        info_dict = kwargs['kwargs']
        cpu_rate = info_dict['cpu_range']
        memery_rate = info_dict['memery_range']
        if cpu_rate['busy'] > 10 or memery_rate['busy'] > 10:
            state = 'busy'
        elif cpu_rate['idle'] > 95 or memery_rate['idle'] > 95:
            state = 'idle'
        else:
            state = 'normal'
        vmstates = self.format_instance(instance, state, kwargs=info_dict)
        return vmstates
    def format_instance(self,obj,state,**kwargs):
        instance_info = {}
        extend = kwargs['kwargs']
        instance_info['instance_id'] = obj.id
        instance_info['state'] = state
        instance_info['instance_name'] = getattr(obj, 'name')
        instance_info['instance_name'] = obj.name
        if getattr(obj, 'OS-EXT-STS:vm_state') not in ['deleted', 'building']:
            addr_info = obj.addresses['ext-net']
            instance_info['ip'] = addr_info[0]['addr']
        else:
            instance_info['ip'] = None
        instance_info['cluster'] = getattr(obj, 'OS-EXT-AZ:availability_zone')
        instance_info['cpu_range'] = extend['cpu_range']
        instance_info['cpu_util'] = extend['cpu_util']
        instance_info['memory_range'] = extend['memory_range']
        instance_info['memory_util'] = extend['memory_util']
        instance_info['flavor'] = extend['flavor']
        instance_info['os_type'] = None
        return instance_info

class project_vmstatistc(instance_help_base):
    
    def __init__(self, timeStart, timeEnd):
        super(project_vmstatistc, self).__init__(timeStart,timeEnd)
    
    def Get_VM_State_dict(self,project_id):
        
	vm_dict = {'project_id': project_id,
                   'normal': 0,
                   'busy': 0,
                   'idle': 0,
                   'suspended': 0,
                   'stop': 0}
        return vm_dict


#get every instance state
#return generator of instance states
def get_instance_states(timeStart,timeEnd):
        statistic_info={}
        help = state_help(timeStart,timeEnd)
        instance_list=help.get_all_instance_in_timestamp()
        for instance in instance_list:
            interval=help.Get_real_timestamp(instance)
            if interval == 0:
                continue
            boot_time=help.get_instance_boot_time(instance,timeStart,timeEnd)
            run_rate=(boot_time/interval )*100
            if run_rate < 5:
                stop_instance=help.format_instance(instance,'stop',kwargs=statistic_info)
                yield stop_instance
            else:
                query = help.sample_query(timeStart, timeEnd, instance.id)
                instance_samples = help.sample_operation(query)
                flavor = help.Get_Flavor_Info(instance.flavor['id'])
                util_dict = help.get_util_from_sample(flavor.ram, instance_samples)
                statistic_info['cpu_range'] = help.Get_Cpu_Util_Info(timeStart, timeEnd, instance.id)
                if help.Is_suspended_state(timeStart,timeEnd,instance.id,statistic_info['cpu_range']):
                    suspend_instance = help.format_instance(instance, 'suspended', kwargs=statistic_info)
                    yield  suspend_instance
                else:
                    statistic_info['cpu_util'] = help.rate_cal(util_dict['cpu_util'])
                    statistic_info['memory_util'] = help.rate_cal(util_dict['memory_util'])
                    instance_state=help.calculate_state(instance,kwargs=statistic_info)
                    yield instance_state


def Get_VM_Statistic(timeStart,timeEnd):
    statistic_info = {}
    help = vm_statistic_help(timeStart, timeEnd)
    instance_list = help.get_all_instance_in_timestamp()
    for instance in instance_list:
        interval = help.Get_real_timestamp(instance)
        if interval == 0:
            continue
        boot_time = help.get_instance_boot_time(instance, timeStart, timeEnd)
        run_rate = (boot_time / interval) * 100
        query = help.sample_query(timeStart, timeEnd, instance.id)
        instance_samples = help.sample_operation(query)
        flavor=help.Get_Flavor_Info(instance.flavor['id'])
        util_dict = help.get_util_from_sample(flavor.ram, instance_samples)
        statistic_info['cpu_range'] = help.rate_cal(util_dict['cpu_util'])
        statistic_info['cpu_util'] = help.Get_Cpu_Util_Info(timeStart, timeEnd, instance.id)
        statistic_info['memory_range'] = help.rate_cal(util_dict['memory_util'])
        statistic_info['memory_util'] = help.Get_Memory_Util_Info(timeStart, timeEnd, instance.id, flavor.ram)
        statistic_info['flavor']=dict(ram=flavor.ram,cpu=flavor.vcpus,disk=flavor.disk)
        if run_rate < 5:
            stop_instance_info = help.format_instance(instance, 'stop', kwargs=statistic_info)
            yield stop_instance_info
        else:
            if help.Is_suspended_state(timeStart, timeEnd, instance.id, statistic_info['cpu_util']):
                suspend_instance_info = help.format_instance(instance, 'suspended', kwargs=statistic_info)
                yield suspend_instance_info
            else:
                instance_state_info = help.calculate_state(instance,kwargs=statistic_info)
                yield instance_state_info



def Get_Project_With_Vmstates(timeStart,timeEnd):
    project_list=[]
    vm_pro_map={}
    help=project_vmstatistc(timeStart,timeEnd)
    instance_list=help.get_all_instance_in_timestamp()
    if len(instance_list)!=0:
        for instance in instance_list:
            if instance.tenant_id not in project_list:
                project_list.append(instance.tenant_id)
                vm_pro_map[instance.tenant_id]=list()
            else:
                vm_pro_map[instance.tenant_id].append(instance)
        for project,instance_list in vm_pro_map.items():
            vm_dict=help.Get_VM_State_dict(project)
            for instance in instance_list:
                interval = help.Get_real_timestamp(instance)
                if interval == 0:
                    continue
                boot_time=help.get_instance_boot_time(instance,timeStart,timeEnd)
                run_rate=(boot_time/interval )*100
                if run_rate < 5:
                    vm_dict['stop']+=1
                else:
                    query = help.sample_query(timeStart, timeEnd, instance.id)
                    instance_samples = help.sample_operation(query)
                    flavor = help.Get_Flavor_Info(instance.flavor['id'])
                    util_dict = help.get_util_from_sample(flavor.ram, instance_samples)
                    cpu_range= help.Get_Cpu_Util_Info(timeStart, timeEnd, instance.id)
                    if help.Is_suspended_state(timeStart, timeEnd, instance.id, cpu_range):
                       vm_dict['suspended']+=1
                    else:
                        cpu_rate = help.rate_cal(util_dict['cpu_util'])
                        memery_rate = help.rate_cal(util_dict['memory_util'])
                        if cpu_rate['busy'] > 10 or memery_rate['busy'] > 10:
                           vm_dict['busy']+=1
                        elif cpu_rate['idle'] > 95 or memery_rate['idle'] > 95:
                            vm_dict['idle'] += 1
                        else:
                            vm_dict['normal'] += 1
            yield vm_dict

def verify_time_parameter(timeStart,timeEnd):
    try:
        timeS=timeutils.parse_isotime(timeStart)
        timeE=timeutils.parse_isotime(timeEnd)
        if timeS>timeE:
            raise wsme.exc.InvalidInput(fieldname="invalidinput",msg='timeStart is bigger than timeEnd')
    except ValueError:
        raise wsme.exc.InvalidInput(fieldname="invalidinput",msg='time format is not utc')

class instancestatesController(rest.RestController):
    _custom_actions = {
        'state':['GET'],
        'vm_statistic':['GET'],
        'project_vmstate':['GET']
    }
    @wsme_pecan.wsexpose([instancestates],str,str)
    def state(self, timeStart=None, timeEnd=None):
        rbac.enforce('get_instance_states', pecan.request)
        if timeStart is None or timeEnd is None:
            raise wsme.exc.MissingArgument(argname="missingArg", msg='must input timeStart timeEnd')
        else:
            verify_time_parameter(timeStart, timeEnd)
            return map(instancestates.format,get_instance_states(timeStart,timeEnd))

    @wsme_pecan.wsexpose([vmstatisticsinfo], str, str)
    def vm_statistic(self,timeStart=None, timeEnd=None):
        rbac.enforce('get_vm_statistic', pecan.request)
        if timeStart is None or timeEnd is None:
            raise wsme.exc.MissingArgument(argname="missingArg", msg='must input timeStart timeEnd')
        else:
            verify_time_parameter(timeStart, timeEnd)
            return map(vmstatisticsinfo.format, Get_VM_Statistic(timeStart, timeEnd))

    @wsme_pecan.wsexpose([projectwithvmstate], str, str)
    def project_vmstate(self,timeStart,timeEnd):
        rbac.enforce('get_project_vmstates', pecan.request)
        if timeStart is None or timeEnd is None:
            raise wsme.exc.MissingArgument(argname="missingArg", msg='must input timeStart timeEnd')
        else:
            verify_time_parameter(timeStart,timeEnd)
            return map(projectwithvmstate.format,Get_Project_With_Vmstates(timeStart,timeEnd))



