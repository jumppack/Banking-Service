from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.account import Account
from app.schemas.transfer import TransferCreate
from app.services.transfer_service import TransferService

router = APIRouter(prefix="/transfers", tags=["transfers"])

@router.post("/", status_code=status.HTTP_200_OK)
async def create_transfer(
    transfer_in: TransferCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    # Fetch from_account to verify ownership
    result = await session.execute(select(Account).where(Account.id == transfer_in.from_account_id))
    from_account = result.scalar_one_or_none()
    
    if not from_account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source account not found")
        
    if from_account.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to transfer from this account")
        
    try:
        await TransferService.transfer_funds(
            from_account_id=transfer_in.from_account_id,
            to_account_id=transfer_in.to_account_id,
            amount=transfer_in.amount,
            session=session
        )
        return {"status": "success", "message": "Transfer completed successfully"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
