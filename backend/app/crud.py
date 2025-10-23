from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from . import models, schemas


# ============ Account CRUD ============
def get_account(db: Session, account_id: int) -> models.Account:
    """Get single account by ID"""
    account = db.query(models.Account).filter(models.Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account


def get_accounts(db: Session, skip: int = 0, limit: int = 100) -> list[models.Account]:
    """Get all accounts with pagination"""
    return db.query(models.Account).offset(skip).limit(limit).all()


def get_user_accounts(db: Session, user_id: int) -> list[models.Account]:
    """Get all accounts for a specific user"""
    # Verify user exists
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return db.query(models.Account).filter(models.Account.user_id == user_id).all()


def create_account(db: Session, account: schemas.AccountCreate) -> models.Account:
    """Create new account for a user"""
    # Verify user exists
    user = db.query(models.User).filter(models.User.id == account.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db_account = models.Account(**account.model_dump())
    try:
        db.add(db_account)
        db.commit()
        db.refresh(db_account)
        return db_account
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Account for provider '{account.provider.value}' already exists for this user"
        )


def update_account(db: Session, account_id: int, account: schemas.AccountUpdate) -> models.Account:
    """Update existing account"""
    db_account = get_account(db, account_id)
    update_data = account.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(db_account, field, value)

    db.commit()
    db.refresh(db_account)
    return db_account


def delete_account(db: Session, account_id: int) -> None:
    """Delete account"""
    db_account = get_account(db, account_id)
    db.delete(db_account)
    db.commit()
