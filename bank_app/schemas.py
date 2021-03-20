from typing import List, Optional

from pydantic import BaseModel

from datetime import datetime

'''
    schema for validation input payload and response payload
'''
##
class CustomerBase(BaseModel):
    name: str

class CustomerCreate(CustomerBase):
    name: str


##

class AccountBase(BaseModel):
    cus_id: int

class AccountCreate(AccountBase):
    cus_id: int

##

class TransectionBase(BaseModel):
    ac_source_id: int
    ac_destination_id: int
    amount: int

class TransectionDeposit(BaseModel):
    cus_id: int
    acc_id: int
    amount: int

class TransectionTransfer(BaseModel):
    cus_id: int
    ac_source_id: int
    ac_destination_id: int
    amount: int




# response schema for matching

class Transection(TransectionBase):
    id: int
    ac_source_id: int
    ac_destination_id: int
    amount: int
    transection_state: str
    crt_dtm: datetime
    update_dtm: datetime
    class Config:
        orm_mode = True

class Account(AccountBase):
    id: int
    cus_id: int
    ac_balance: int    
    crt_dtm: datetime
    update_dtm: datetime
    transection_deposit: List[Transection] = []
    transection_transfer_out: List[Transection] = []
    transection_transfer_in: List[Transection] = []
    class Config:
        orm_mode = True

class Customer(CustomerBase):
    id: int
    name: str
    cs_balance: int
    crt_dtm: datetime
    update_dtm: datetime
    accounts: List[Account] = []
    class Config:
        orm_mode = True