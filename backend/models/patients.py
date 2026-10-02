from sqlalchemy import Column, Integer, String

from db.connection import Base


class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    phone_number = Column(String, nullable=False)


