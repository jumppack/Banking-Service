from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.account import Account
from app.schemas.transfer import TransferCreate
from app.services.transfer_service import TransferService
import uuid
from app.api.helpers import get_valid_account

router = APIRouter(prefix="/transfers", tags=["transfers"])

@router.post(
    "/", 
    status_code=status.HTTP_200_OK,
    summary="Execute internal fund transfer",
    description="Transfers funds from the authenticated user's account to a counterparty account (resolvable by UUID or Email). Guaranteed mathematically by strict Double-Entry Logic inside a database transaction.",
    response_description="A success confirmation wrapper."
)
async def create_transfer(
    transfer_in: TransferCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    # Fetch and strictly verify ownership of the source account before proceeding
    from_account = await get_valid_account(session, transfer_in.from_account_id, current_user.id, "Not authorized to transfer from this account")
        
    to_account_id = None
    try:
        to_account_id = uuid.UUID(transfer_in.to_identifier)
    except ValueError:
        # Not a valid UUID; assume it's an email search string
        user_result = await session.execute(select(User).where(User.email == transfer_in.to_identifier))
        to_user = user_result.scalar_one_or_none()
        
        if not to_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Destination user not found via email")
            
        accounts_result = await session.execute(select(Account).where(Account.user_id == to_user.id))
        user_accounts = accounts_result.scalars().all()
        
        if not user_accounts:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Destination user has no active accounts")
            
        # Safely prioritize pushing funds into their primary checking (100) or gracefully falling back
        primary_acc = next((a for a in user_accounts if a.account_number.startswith("100")), user_accounts[0])
        to_account_id = primary_acc.id

    try:
        await TransferService.transfer_funds(
            from_account_id=transfer_in.from_account_id,
            to_account_id=to_account_id,
            amount=transfer_in.amount,
            session=session
        )
        return {"status": "success", "message": "Transfer completed successfully"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
