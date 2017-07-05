from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, Boolean

#import images tables
from glance.db.sqlalchemy.models import ImageTemplate, ImageTemplatesGroup

from nova.db.sqlalchemy.test_db_connection import get_image_uuid_from_imagegroup

#connection to mysql
sql_connection = "mysql+pymysql://glance:123456@controller/glance?charset=utf8"
engine = create_engine(sql_connection, echo=True)
Session = sessionmaker(bind=engine)
session = Session()

#connection to mysql
sql_connection = "mysql+pymysql://glance:123456@controller/glance?charset=utf8"
engine = create_engine(sql_connection, echo=True)
Session = sessionmaker(bind=engine)
session = Session()

def get_imageid_from_imageflavor_name(group_imageflavor_name):
    image_uuid = []
    for imageflavor_name in group_imageflavor_name:
        print ("imageflavor_name = %s"%imageflavor_name)
        imageid=session.query(ImageTemplate).filter_by(template_name=imageflavor_name).first().image_id
        print("imageid=%s"%imageid)
        image_uuid.append(imageid)
    return image_uuid

def get_image_uuid_from_imagegroup(uuid):
    groupstr=session.query(ImageTemplatesGroup).filter_by(id=uuid).first().group_members
    group_imageflavor_name=groupstr.split(",")
    image_uuid=get_imageid_from_imageflavor_name(group_imageflavor_name)
    return image_uuid

uuid=1
image_uuid=get_image_uuid_from_imagegroup(uuid)
print("image_uuid = %s"%image_uuid)
for i in image_uuid:
    print i
