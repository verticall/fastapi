from typing import List

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import SessionLocal, engine


models.Base.metadata.create_all(bind=engine)


app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# customer
@app.get("/customers/", response_model=List[schemas.Customer])
def read_customers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    customers = crud.get_customers(db, skip=skip, limit=limit)
    return customers


@app.post("/customer/", response_model=schemas.Customer)
def create_user(customer: schemas.CustomerCreate, db: Session = Depends(get_db)):
    # check customer dupplicate name
    db_cus = crud.get_customer_by_name(db, name=customer.name)
    if db_cus:
        raise HTTPException(status_code=400, detail="Customer already registered")
    return crud.create_customer(db=db, customer=customer)


@app.post("/customer/{cus_id}/account", response_model=schemas.Account)
def create_account(cus_id: int, db: Session = Depends(get_db)):
    db_cus = crud.get_customer_by_id(db, cus_id=cus_id)
    if not db_cus:
        raise HTTPException(status_code=400, detail="Customer id not found.")
    return crud.create_account(db=db, cus_id=cus_id)


@app.get("/customer/account/transection", response_model=List[schemas.Account])
def get_transection(cus_id: int = 0, ac_id: int = 0, db: Session = Depends(get_db)):
    return crud.get_transection(db=db,cus_id=cus_id,ac_id=ac_id)


@app.post("/customer/account/deposit", response_model=schemas.Transection)
def deposit_transection(
    deposit: schemas.TransectionDeposit, db: Session = Depends(get_db)
):
    # check exists customer_id
    if not crud.get_customer_by_id(db, cus_id=deposit.cus_id):
        raise HTTPException(status_code=400, detail="Customer id not found.")

    # check customer_id match account source id
    if not crud.get_customer_by_cus_id_and_acc_id(db, deposit.cus_id, deposit.acc_id):
        raise HTTPException(status_code=400, detail="Account id not valid.")

    # check amount negative value
    if deposit.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount not valid.")
    return crud.deposit_transection(
        db, transection=deposit, transection_state="deposit"
    )


@app.post("/customer/account/transfer", response_model=schemas.Transection)
def transfer_transection(
    transfer: schemas.TransectionTransfer, db: Session = Depends(get_db)
):
    # check exists customer_id
    if not crud.get_customer_by_id(db, cus_id=transfer.cus_id):
        raise HTTPException(status_code=400, detail="Customer id not found.")

    # check customer_id match account source id
    if not crud.get_customer_by_cus_id_and_acc_id(
        db, transfer.cus_id, transfer.ac_source_id
    ):
        raise HTTPException(status_code=400, detail="Source Account id not valid.")

    # check exists account destination id
    if not crud.get_account_info_by_id(db, transfer.ac_destination_id):
        raise HTTPException(status_code=400, detail="Destination Account id not valid.")

    # check transfer dupplicate account id
    if transfer.ac_source_id == transfer.ac_destination_id:
        raise HTTPException(
            status_code=400, detail="Source and Destination Account id not valid."
        )

    # check amount negative value
    if transfer.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount not valid.")

    # check source balance for transfer
    if (
        crud.get_account_info_by_id(db, transfer.ac_source_id).ac_balance
        < transfer.amount
    ):
        raise HTTPException(
            status_code=400, detail="Source Account Balance Not enough."
        )

    return crud.transfer_transection(
        db, transfer=transfer, transection_state="transfer"
    )
