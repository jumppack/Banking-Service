import uuid
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.account import Account

async def get_valid_account(session: AsyncSession, account_id: uuid.UUID, current_user_id: uuid.UUID, forbidden_msg: str = "Not authorized to access this account") -> Account:
    """Helper to verify an account exists and uniquely belongs to the current authenticated user."""
    result = await session.execute(select(Account).where(Account.id == account_id))
    account = result.scalar_one_or_none()
    
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
        
    if account.user_id != current_user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=forbidden_msg)
        
    return account
