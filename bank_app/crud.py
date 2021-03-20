from sqlalchemy.orm import Session

from . import models, schemas

from datetime import datetime

"""
    query builder
"""

# customer


def create_customer(db: Session, customer: schemas.CustomerCreate):
    _args = dict()
    _args["name"] = customer.name
    _args["crt_dtm"] = datetime.now()  # inject field
    _args["update_dtm"] = datetime.now()  # inject field
    db_customer = models.Customer(**_args)
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer


def get_customer_by_name(db: Session, name: str):
    return db.query(models.Customer).filter(models.Customer.name == name).first()


def get_customer_by_id(db: Session, cus_id: int):
    return db.query(models.Customer).filter(models.Customer.id == cus_id).first()


def get_customer_by_cus_id_and_acc_id(db: Session, cus_id: int, acc_id: int):
    # return list(map(lambda item:item if item.cus_id == cus_id and item.id == acc_id else dict(), db.query(models.Account).all()))
    return (
        db.query(models.Account)
        .filter(models.Account.cus_id == cus_id)
        .filter(models.Account.id == acc_id)
        .first()
    )


def get_customers(db: Session, skip: int = 0, limit: int = 100):
    obj_query = db.query(models.Customer).offset(skip).limit(limit)
    _result = obj_query.all()
    for cus in _result:
        for acc in cus.accounts:
            acc.transection_deposit = (
                db.query(models.Transection)
                .filter(models.Transection.ac_source_id == acc.id)
                .filter(models.Transection.transection_state == "deposit")
                .all()
            )
            acc.transection_transfer_out = (
                db.query(models.Transection)
                .filter(models.Transection.ac_source_id == acc.id)
                .filter(models.Transection.transection_state == "transfer")
                .all()
            )
            acc.transection_transfer_in = (
                db.query(models.Transection)
                .filter(models.Transection.ac_destination_id == acc.id)
                .filter(models.Transection.transection_state == "transfer")
                .all()
            )
    return _result


# account


def get_account_info_by_id(db: Session, acc_id: int):
    return db.query(models.Account).filter(models.Account.id == acc_id).first()


def create_account(db: Session, cus_id: int):
    _args = dict()
    _args["cus_id"] = cus_id
    _args["crt_dtm"] = datetime.now()  # inject field
    _args["update_dtm"] = datetime.now()  # inject field
    db_account = models.Account(**_args)
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account


# transection


def get_transection(db: Session, cus_id: int, ac_id: int):
    obj_query = db.query(models.Account)
    if cus_id > 0:
        obj_query = obj_query.filter(models.Account.cus_id == cus_id)
    if ac_id > 0:
        obj_query = obj_query.filter(models.Account.id == ac_id)
    #
    # append transection to account
    #
    _result = obj_query.all()
    for doc in _result:
        doc.transection_deposit = (
            db.query(models.Transection)
            .filter(models.Transection.ac_source_id == doc.id)
            .filter(models.Transection.transection_state == "deposit")
            .all()
        )
        doc.transection_transfer_out = (
            db.query(models.Transection)
            .filter(models.Transection.ac_source_id == doc.id)
            .filter(models.Transection.transection_state == "transfer")
            .all()
        )
        doc.transection_transfer_in = (
            db.query(models.Transection)
            .filter(models.Transection.ac_destination_id == doc.id)
            .filter(models.Transection.transection_state == "transfer")
            .all()
        )
    return _result


def deposit_transection(
    db: Session, transection: schemas.TransectionDeposit, transection_state: str
):
    _args = dict()
    _args["ac_source_id"] = transection.acc_id
    _args["ac_destination_id"] = transection.acc_id
    _args["amount"] = transection.amount
    _args["transection_state"] = transection_state
    _args["crt_dtm"] = datetime.now()  # inject field
    _args["update_dtm"] = datetime.now()  # inject field
    db_transection = models.Transection(**_args)
    db.add(db_transection)
    db.commit()
    db.refresh(db_transection)

    # pipeline update balance account
    account = (
        db.query(models.Account).filter(models.Account.id == transection.acc_id).first()
    )
    cus_id = account.cus_id
    account.ac_balance += transection.amount
    account.update_dtm = datetime.now()
    db.commit()
    db.refresh(account)

    # pipeline update balance customer
    customer = db.query(models.Customer).filter(models.Customer.id == cus_id).first()
    customer.cs_balance += transection.amount
    customer.update_dtm = datetime.now()
    db.commit()
    db.refresh(customer)

    return db_transection


def transfer_transection(
    db: Session, transfer: schemas.TransectionTransfer, transection_state: str
):
    _args = dict()
    _args["ac_source_id"] = transfer.ac_source_id
    _args["ac_destination_id"] = transfer.ac_destination_id
    _args["amount"] = transfer.amount
    _args["transection_state"] = transection_state
    _args["crt_dtm"] = datetime.now()  # inject field
    _args["update_dtm"] = datetime.now()  # inject field
    db_transection = models.Transection(**_args)
    db.add(db_transection)
    db.commit()
    db.refresh(db_transection)

    # pipeline update balance source
    # account
    source_account_info = get_account_info_by_id(db, transfer.ac_source_id)
    account = (
        db.query(models.Account)
        .filter(models.Account.id == source_account_info.id)
        .first()
    )
    account.ac_balance -= transfer.amount
    account.update_dtm = datetime.now()
    db.commit()
    db.refresh(account)
    # customer
    customer = (
        db.query(models.Customer)
        .filter(models.Customer.id == source_account_info.cus_id)
        .first()
    )
    customer.cs_balance -= transfer.amount
    customer.update_dtm = datetime.now()
    db.commit()
    db.refresh(customer)

    # pipeline update balance destination
    destination_account_info = get_account_info_by_id(db, transfer.ac_destination_id)
    # account
    account = (
        db.query(models.Account)
        .filter(models.Account.id == destination_account_info.id)
        .first()
    )
    account.ac_balance += transfer.amount
    account.update_dtm = datetime.now()
    db.commit()
    db.refresh(account)
    # customer
    customer = (
        db.query(models.Customer)
        .filter(models.Customer.id == destination_account_info.cus_id)
        .first()
    )
    customer.cs_balance += transfer.amount
    customer.update_dtm = datetime.now()
    db.commit()
    db.refresh(customer)

    return db_transection
