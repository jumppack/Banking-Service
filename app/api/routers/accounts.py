from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid

from app.db.session import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.account import Account
from app.schemas.account import AccountCreate, AccountResponse

router = APIRouter(prefix="/accounts", tags=["accounts"])

@router.post("/", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
async def create_account(
    currency: str = "USD",
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    account_number = str(uuid.uuid4().hex)[:10]  # Simple random account number generator
    new_account = Account(
        user_id=current_user.id,
        account_number=account_number,
        currency=currency,
        balance=0
    )
    session.add(new_account)
    await session.commit()
    await session.refresh(new_account)
    return new_account

@router.get("/me", response_model=List[AccountResponse])
async def get_my_accounts(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    result = await session.execute(select(Account).where(Account.user_id == current_user.id))
    accounts = result.scalars().all()
    return accounts

@router.get("/{account_id}", response_model=AccountResponse)
async def get_account(
    account_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    result = await session.execute(select(Account).where(Account.id == account_id))
    account = result.scalar_one_or_none()
    
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
        
    if account.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this account")
        
    return account
