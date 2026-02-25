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

@router.post(
    "/", 
    response_model=AccountResponse, 
    status_code=status.HTTP_201_CREATED,
    summary="Open a new bank account",
    description="Automatically generates a unique 10-digit account number and attaches it to the currently authenticated user.",
    response_description="The newly created Account entity, initialized with a 0 balance."
)
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

@router.get(
    "/me", 
    response_model=List[AccountResponse],
    summary="List my accounts",
    description="Returns an array of all financial accounts linked to the currently authenticated user session.",
    response_description="A list of Account objects. Empty if none exist."
)
async def get_my_accounts(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    result = await session.execute(select(Account).where(Account.user_id == current_user.id))
    accounts = result.scalars().all()
    return accounts

@router.get(
    "/{account_id}", 
    response_model=AccountResponse,
    summary="Get account details by ID",
    description="Fetches real-time details (including current balance) for a specific account. Fails if the account does not belong to the user.",
    response_description="The specific Account entity requested."
)
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
