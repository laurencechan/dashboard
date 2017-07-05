from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, Boolean

from nova.db.sqlalchemy.models import Instance
#from glance
#import images tables
from glance.db.sqlalchemy.models import ImageTemplate, ImageTemplatesGroup

#connection to mysql
#sql_connection = "mysql://root:root@localhost/nova?charset=utf8"
#sql_connection = "mysql+pymysql://nova:123456@controller/nova?charset=utf8"
sql_connection = "mysql+pymysql://glance:123456@controller/glance?charset=utf8"
engine = create_engine(sql_connection, echo=True)
Session = sessionmaker(bind=engine)
session = Session()

def get_imageid_from_imageflavor_name(group_imageflavor_name):
    image_uuid = []
    for imageflavor_name in group_imageflavor_name:
        imageid=session.query(ImageTemplate).filter_by(template_name=imageflavor_name).first().image_id
        image_uuid.appand(imageid)
    return image_uuid

#def get_flavorid_from_imageflavor_name(group_imageflavor_name):
#    flavor_uuid = []
#    for imageflavor_name in group_imageflavor_name:
#        flavorid=session.query(ImageTemplate).filter_by(template_name=imageflavor_name).first().flavor_id
#        flavor_uuid.appand(flavorid)
#    return flavor_uuid

def get_image_uuid_from_imagegroup(uuid):
    groupstr=session.query(ImageTemplatesGgroup).filter_by(id=uuid).first().templete_groups
    group_imageflavor_name=groupstr.split(",")
    image_uuid=get_imageid_from_imageflavor_name(group_imageflavor_name)
    return image_uuid

#def get_flavor_uuid_from_imagegroup(uuid):
#    groupstr=session.query(ImageTemplatesGgroup).filter_by(id=uuid).first().templete_groups
#    group_imageflavor_name=groupstr.split(",")
#    flavor_uuid=get_flavorid_from_imageflavor_name(group_imageflavor_name)
