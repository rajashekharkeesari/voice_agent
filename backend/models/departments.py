from sqlalchemy import Column, Integer, String

from backend.db.connection import Base

class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
   