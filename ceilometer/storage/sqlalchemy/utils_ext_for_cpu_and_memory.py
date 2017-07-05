# coding=utf-8

from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Index
from sqlalchemy import Integer
from sqlalchemy import orm
from sqlalchemy import schema
from sqlalchemy import String, VARCHAR, DateTime
from sqlalchemy.ext.declarative import declarative_base

"""
@author hy
@date 17/6/19
用于读取集群下所有计算节点的实例
"""
Base = declarative_base()
nova_engine = create_engine("mysql+pymysql://root:123456@10.172.10.10:3306/nova")
nova_api_engine = create_engine("mysql+pymysql://root:123456@10.172.10.10:3306/nova_api")
nova_DBSession = sessionmaker(bind=nova_engine)
nova_api_DBSession = sessionmaker(bind=nova_api_engine)


class AggregateHost(Base):
    """Represents a host that is member of an aggregate."""
    __tablename__ = 'aggregate_hosts'
    __table_args__ = (schema.UniqueConstraint(
        "host", "aggregate_id",
        name="uniq_aggregate_hosts0host0aggregate_id"
    ),
    )
    id = Column(Integer, primary_key=True, autoincrement=True)
    host = Column(String(255))
    aggregate_id = Column(Integer, ForeignKey('aggregates.id'), nullable=False)


class AggregateMetadata(Base):
    """Represents a metadata key/value pair for an aggregate."""
    __tablename__ = 'aggregate_metadata'
    __table_args__ = (
        schema.UniqueConstraint("aggregate_id", "key",
                                name="uniq_aggregate_metadata0aggregate_id0key"
                                ),
        Index('aggregate_metadata_key_idx', 'key'),
    )
    id = Column(Integer, primary_key=True)
    key = Column(String(255), nullable=False)
    value = Column(String(255), nullable=False)
    aggregate_id = Column(Integer, ForeignKey('aggregates.id'), nullable=False)


class Aggregate(Base):
    """Represents a cluster of hosts that exists in this zone."""
    __tablename__ = 'aggregates'
    __table_args__ = (Index('aggregate_uuid_idx', 'uuid'),
                      schema.UniqueConstraint(
                          "name", name="uniq_aggregate0name")
                      )
    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(String(36))
    name = Column(String(255))
    _hosts = orm.relationship(AggregateHost,
                              primaryjoin='Aggregate.id == AggregateHost.aggregate_id',
                              cascade='delete')
    _metadata = orm.relationship(AggregateMetadata,
                                 primaryjoin='Aggregate.id == AggregateMetadata.aggregate_id',
                                 cascade='delete')

    @property
    def _extra_keys(self):
        return ['hosts', 'metadetails', 'availability_zone']

    @property
    def hosts(self):
        return [h.host for h in self._hosts]

    @property
    def metadetails(self):
        return {m.key: m.value for m in self._metadata}

    @property
    def availability_zone(self):
        if 'availability_zone' not in self.metadetails:
            return None
        return self.metadetails['availability_zone']


class Instance(Base):
    """Represents a guest VM."""
    __tablename__ = 'instances'
    created_at = Column()
    updated_at = Column(String(100))
    deleted_at = Column(String(100))
    internal_id = Column(Integer)
    user_id = Column(VARCHAR(255))
    project_id = Column(VARCHAR(255))
    image_ref = Column(VARCHAR(255))
    kernel_id = Column(VARCHAR(255))
    ramdisk_id = Column(VARCHAR(255))
    launch_index = Column(Integer)
    key_name = Column(VARCHAR(255))
    key_data = Column(VARCHAR(255))
    power_state = Column(Integer)
    vm_state = Column(VARCHAR(255))
    memory_mb = Column(Integer)
    vcpus = Column(Integer)
    hostname = Column(VARCHAR(255))
    host = Column(VARCHAR(255))
    user_data = Column(VARCHAR(255))
    reservation_id = Column(VARCHAR(255))
    scheduled_at = Column(DateTime)
    launched_at = Column(DateTime)
    terminated_at = Column(DateTime)
    display_name = Column(VARCHAR(255))
    display_description = Column(VARCHAR(255))
    availability_zone = Column(VARCHAR(255))
    locked = Column(VARCHAR(10))
    os_type = Column(VARCHAR(255))
    launched_on = Column(VARCHAR(255))
    instance_type_id = Column(Integer)
    vm_mode = Column(VARCHAR(255))
    uuid = Column(VARCHAR(255))
    architecture = Column(VARCHAR(255))
    root_device_name = Column(VARCHAR(255))
    access_ip_v4 = Column(VARCHAR(255))
    access_ip_v6 = Column(VARCHAR(255))
    config_drive = Column(VARCHAR(255))
    task_state = Column(VARCHAR(255))
    default_ephemeral_device = Column(VARCHAR(255))
    default_swap_device = Column(VARCHAR(255))
    progress = Column(Integer)
    auto_disk_config = Column(VARCHAR(10))
    shutdown_terminate = Column(VARCHAR(10))
    disable_terminate = Column(VARCHAR(10))
    root_gb = Column(Integer)
    ephemeral_gb = Column(Integer)
    cell_name = Column(VARCHAR(255))
    node = Column(VARCHAR(255))
    deleted = Column(Integer)
    locked_by = Column(VARCHAR(50))
    cleaned = Column(Integer)
    ephemeral_key_uuid = Column(VARCHAR(36))
    id = Column(Integer, primary_key=True)


class ComputeNode(Base):
    __tablename__ = 'compute_nodes'
    id = Column(Integer, primary_key=True)
    host_ip = Column(VARCHAR(50))#节点ip
    host = Column(VARCHAR(255))#节点名称


def query_ip_of_compute_from_cluster(cluster):
    """
    查询集群对应的实例
    :param cluster: 
    :return: 
    """
    try:
        nova_session = nova_DBSession()
        # nova_api_session = nova_api_DBSession()
        # # 获取集群
        # cluster_item = nova_api_session.query(Aggregate).filter(Aggregate.name == cluster).one()
        # # 获取计算节点
        # compute_hosts = nova_api_session.query(AggregateHost).filter(
        #     AggregateHost.aggregate_id == cluster_item.id).all()
        # if 0 == len(compute_hosts):
        #     raise NoResultFound()
        # 获取计算节点名称
        # compute_hosts = [item.host for item in compute_hosts]
        ips = []
        compute_hosts=cluster
        for host in compute_hosts:
            try:
               node = nova_session.query(ComputeNode).filter(ComputeNode.host == host).one()
            except Exception:
                raise NoResultFound
            ips.append(node.host_ip)
        nova_session.close()
       # nova_api_session.close()
        return ips
    except SQLAlchemyError as err:
        err.message = "连接数据库异常"
        raise err
    except NoResultFound as err:
        err.message = "不存在该集群"
        raise err
    except MultipleResultsFound as err:
        err.message = "数据库异常，存在多个相同的集群"
        raise err
    except Exception as err:
        err.message = "未处理的异常"
        raise err


if __name__ == "__main__":
    query_ip_of_compute_from_cluster(["compute1","compute2"])
