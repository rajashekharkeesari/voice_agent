from sqlalchemy import Column,Boolean,Integer,String ,ForeignKey
from backend.db.connection import Base

class HospitalService(Base):
    __tablename__ = "Hospital"
   
    id = Column(Integer, primary_key=True, index=True)
    Hospital_name = Column(String,nullable = False)
    contact_no = Column(String)
    is_active = Column(Boolean,default= False)
 