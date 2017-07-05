# coding=utf-8
# 关于性能方面的相关计算，比如cpu,内存，存储等方面的利用率，总量，使用量等

# hy
# 2017/6/29

from pecan import rest
import wsmeext.pecan as wsme_pecan
from ceilometer.api.controllers.v2 import base
import wsme
from datetime import datetime
from ceilometer import storage
import pecan
from ceilometer.api.controllers.v2 import utils as v2_utils


class Capability(base.Base):
    """
    对应的性能结果
    """
    cpu_util = [float]
    memory_util = [float]
    disk_read_rate = [float]
    disk_write_rate = [float]
    network_read_rate = [float]
    network_write_rate = [float]
    memory_total = [float]
    memory_usage = [float]

    def __init__(self, startTime, endTime, timeType):
        delta = endTime - startTime
        delta = delta.days + 1  # 因为最后一天要计算进去
        if timeType == "hour":
            self.__init_group_value(delta * 24)
        if timeType == "day":
            self.__init_group_value(delta)
        if timeType == "month":
            if startTime.year == endTime.year:
                self.__init_group_value(endTime.month - startTime.month + 1)
            if startTime.year < endTime.year:
                self.__init_group_value(

                    endTime.month + (endTime.year - startTime.year - 1) * 12 + (12 - startTime.month + 1))

    def __init_group_value(self, length):
        self.cpu_util = [0] * length
        self.memory_util = [0] * length
        self.disk_write_rate = [0] * length
        self.disk_read_rate = [0] * length
        self.network_write_rate = [0] * length
        self.network_read_rate = [0] * length
        self.memory_usage = [0] * length
        self.memory_total = [0] * length


def verify_params(startTime, endTime, timeType):
    """
    验证参数是否合法
    :param startTime: 
    :param endTime: 
    :param timeType: 
    :return: 
    """

    if startTime == None or endTime == None or timeType == None:
        raise wsme.exc.MissingArgument(argname="missingArg", msg='startTime,endTime,timeType are need')
    if timeType not in ('hour', 'day', 'month'):
        raise wsme.exc.UnknownArgument(argname="missingArg", msg='timeType value must be one of {hour,day,month}')
    try:
        startTime += " 00:00:00"
        startTime = datetime.strptime(startTime, "%Y-%m-%d %H:%M:%S")
        endTime += " 23:59:59"
        endTime = datetime.strptime(endTime, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        raise wsme.exc.UnknownArgument(argname="missingArg", msg='time format error,must like that:year-month-day')

    return startTime, endTime, timeType


def get_period_by_timeType(timeType):
    """
    获取对应的时间间隔
    :param timeType: 单位 秒
    :return: 
    """
    # hour表示返回的数据间隔以小时为单位
    # day表示以天为单位
    # month表示以月为单位
    str_to_second = {"hour": 3600, "day": 86400, "month":2592000}
    return str_to_second[timeType]


def get_q_from_condition(resource_uuid, startTime, endTime):
    """
    获取过滤条件
    :param resource_uuid: 
    :param startTime: 
    :param endTime: 
    :return: 
    """
    q = []
    q_item = base.Query()
    q_item.field = "resource_id"
    q_item.type = "string"
    q_item.op = "eq"
    q_item.value = resource_uuid
    q.append(q_item)
    start_item = base.Query()
    start_item.field = "timestamp"
    start_item.op = "le"
    start_item.value = str(endTime)
    q.append(start_item)
    end_item = base.Query()
    end_item.field = "timestamp"
    end_item.op = "ge"
    end_item.value = str(startTime)
    q.append(end_item)
    return q


def set_value_to_result(result=None, data=None, timeType=None, startTime=None, computed=None):
    """
    将值根据日期放到正确的位置上
    :param c: sample值
    :param result: Capability
    :param data: 
    :param timeType: 
    :param startTime: 
    :return: 
    """
    dict_to_result = {"memory": result.memory_total, "cpu_util": result.cpu_util,
                      "disk.read.bytes.rate": result.disk_read_rate,
                      "disk.write.bytes.rate": result.disk_write_rate,
                      "network.incoming.bytes.rate": result.network_read_rate,
                      "network.outgoing.bytes.rate": result.network_write_rate,
                      "memory.usage": result.memory_usage}
    for c in computed:
        time = c.duration_start
        if timeType == "hour":
            delta = ((time - startTime).days) * 24 + time.hour + 1
            dict_to_result[data][delta - 1] = c.avg
        if timeType == "day":
            delta = time - startTime
            dict_to_result[data][delta.days] = c.avg
        if timeType == "month":
            if startTime.year == time.year:
                delta = time.month - startTime.month
                dict_to_result[data][delta] = c.avg
            if time.year > startTime.year:
                delta = (time.year - startTime.year - 1) * 12 + time.month + (12 - startTime.month + 1)
                dict_to_result[data][delta] = c.avg
    return result


class CapabilityController(rest.RestController):
    _custom_actions = {
        'vm': ['GET'],
        'vm_util': ['GET'],
    }

    @wsme_pecan.wsexpose(Capability, str, str, str, str)
    def vm(self, vm_uuid=None, startTime=None, endTime=None, timeType=None):
        """
        获取虚拟机内存使用率，cpu利用率，磁盘读取速率，写速率，网络读速率，写速率
        memory        内存总量
        cpu_util      cpu利用率
        memory.usage  内存使用量
        disk.device.read.bytes.rate 磁盘读取速率
        disk.device.write.bytes.rate 磁盘写速率
        network.incoming.bytes.rate  网络读速率
        network.outgoing.bytes.rate  网络写速率
        :param vm_uuid: 
        :param startTime: 
        :param endTime: 
        :param timeType: {hour,day,month,year}
        :return: 
        """
        if vm_uuid:
            # 验证参数
            startTime, endTime, timeType = verify_params(startTime, endTime, timeType)
            period = get_period_by_timeType(timeType)
            q = get_q_from_condition(vm_uuid, startTime, endTime)
            kwargs = v2_utils.query_to_kwargs(q, storage.SampleFilter.__init__)
            dataType = ["cpu_util", "memory", "memory.usage", "disk.read.bytes.rate",
                        "disk.write.bytes.rate",
                        "network.incoming.bytes.rate",
                        "network.outgoing.bytes.rate"]
            result = Capability(startTime, endTime, timeType)
            # dict_to_result = {"memory": result.memory_total, "cpu_util": result.cpu_util,
            #                   "disk.read.bytes.rate": result.disk_read_rate,
            #                   "disk.write.bytes.rate": result.disk_write_rate,
            #                   "network.incoming.bytes.rate": result.network_read_rate,
            #                   "network.outgoing.bytes.rate": result.network_write_rate,
            #                   "memory.usage": result.memory_usage}
            for data in dataType:
                kwargs['meter'] = data
                f = storage.SampleFilter(**kwargs)
                try:
                    computed = pecan.request.storage_conn.get_meter_statistics(
                        f, period)
                except Exception:
                    continue;
                if (len(computed) != 0):
                    result = set_value_to_result(result, data, timeType, startTime, computed)
            result.memory_util = [
                (result.memory_usage[i] / result.memory_total[i]) * 100 if result.memory_total[i] != 0 else 0 for i in
                range(len(result.memory_total))]
            result.disk_read_rate = [item / 1024 for item in result.disk_read_rate]
            result.disk_write_rate = [item / 1024 for item in result.disk_write_rate]
            result.network_read_rate = [item / 1024 for item in result.network_read_rate]
            result.network_write_rate = [item / 1024 for item in result.network_write_rate]
        else:
            raise wsme.exc.MissingArgument(argname="missingArg", msg='must pass vm_uuid')

        return result

    @wsme_pecan.wsexpose(str)
    def vm_util(self):
        from ceilometer.compute.virt import inspector
        vm_inspector = inspector.get_hypervisor_inspector()
        Instance = inspector.collections.namedtuple('Instance', ['name', 'UUID', 'id'])
        instance = Instance("hy2", "94e67441-b4dc-4e30-880a-87b60947b67d", "94e67441-b4dc-4e30-880a-87b60947b67d")
        cpu_uils = vm_inspector.inspect_cpus(instance)
        disk_info = vm_inspector.inspect_disk_info(instance)
        memeory_usage = vm_inspector.inspect_memory_usage(instance)
        return "ok"
