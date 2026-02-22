from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import uuid

from app.db.session import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.account import Account
from app.schemas.transaction import TransactionResponse
from app.services.account_service import AccountService

router = APIRouter(prefix="/accounts/{account_id}/transactions", tags=["transactions"])

@router.get("/", response_model=List[TransactionResponse])
async def get_transactions(
    account_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    # Verify account ownership first
    result = await session.execute(select(Account).where(Account.id == account_id))
    account = result.scalar_one_or_none()
    
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
        
    if account.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view transactions for this account")
        
    transactions = await AccountService.get_transactions(session, account_id)
    return transactions
