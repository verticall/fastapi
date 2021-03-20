from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship

from .database import Base

'''
    database structure
'''

class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    cs_balance = Column(Integer,default=0)
    crt_dtm = Column(DateTime)
    update_dtm = Column(DateTime)
    accounts = relationship("Account", back_populates="customers")

class Account(Base):
    __tablename__ = "accounts"
    id = Column(Integer, primary_key=True, index=True)
    ac_balance = Column(Integer,default=0)
    cus_id = Column(Integer, ForeignKey("customers.id"))
    customers = relationship("Customer", back_populates="accounts")
    # transections_source = relationship("Transection", back_populates="ac_source")
    # transections_destination = relationship("Transection", back_populates="ac_destination")
    crt_dtm = Column(DateTime)
    update_dtm = Column(DateTime)

class Transection(Base):
    __tablename__ = "transections"
    id = Column(Integer, primary_key=True, index=True)
    ac_source_id = Column(Integer, ForeignKey("accounts.id"))
    ac_destination_id = Column(Integer, ForeignKey("accounts.id"))
    amount = Column(Integer,default=0)
    transection_state = Column(String)
    # ac_source = relationship("Account", back_populates="transections_source")
    # ac_destination = relationship("Account", back_populates="transections_destination")
    crt_dtm = Column(DateTime)
    update_dtm = Column(DateTime)





