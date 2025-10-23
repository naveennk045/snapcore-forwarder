from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
from .. import schemas, crud
from ..dependencies import get_db

router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.post("/", response_model=schemas.AccountResponse, status_code=status.HTTP_201_CREATED)
def create_account(account: schemas.AccountCreate, db: Session = Depends(get_db)):
    """
    Create a new social media account for a user.

    - **user_id**: ID of the user (must exist)
    - **provider**: Social media platform (youtube/facebook/instagram)
    - **post_enabled**: Whether posting is enabled
    - **config**: Provider-specific configuration (e.g., access tokens, page IDs)
    """
    return crud.create_account(db, account)


@router.get("/", response_model=List[schemas.AccountResponse])
def list_accounts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all accounts with pagination"""
    return crud.get_accounts(db, skip=skip, limit=limit)


@router.get("/user/{user_id}", response_model=List[schemas.AccountResponse])
def get_user_accounts(user_id: int, db: Session = Depends(get_db)):
    """Get all accounts for a specific user"""
    return crud.get_user_accounts(db, user_id)


@router.get("/{account_id}", response_model=schemas.AccountResponse)
def get_account(account_id: int, db: Session = Depends(get_db)):
    """Get specific account by ID"""
    return crud.get_account(db, account_id)


@router.patch("/{account_id}", response_model=schemas.AccountResponse)
def update_account(
        account_id: int,
        account: schemas.AccountUpdate,
        db: Session = Depends(get_db)
):
    """
    Update account settings.

    - **post_enabled**: Toggle posting on/off
    - **config**: Update provider configuration
    """
    return crud.update_account(db, account_id, account)


@router.delete("/{account_id}", response_model=schemas.MessageResponse, status_code=status.HTTP_200_OK)
def delete_account(account_id: int, db: Session = Depends(get_db)):
    """Delete account"""
    crud.delete_account(db, account_id)
    return schemas.MessageResponse(message=f"Account {account_id} deleted successfully")
